"""Unified job service — single entry point for triggering and querying ingestion jobs.

All callers (CLI, API, future scheduler, future UI) should go through this service
instead of directly calling store / trigger_runtime / fan_out.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from src.datahub.core.fan_out import build_handler_context, load_plugin_handler, run_handler_async
from src.datahub.core.plugin_loader import find_command, find_plugin_for_job
from src.datahub.core.specs import PluginSpec
from src.datahub.core.trigger_runtime import ExternalSyncClient, new_producer_job_id
from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)

VALID_SOURCES = frozenset({"cli", "api", "scheduler", "ui_manual", "retry"})

RETRYABLE_STATUSES = frozenset({"failed", "partial", "cancelled"})

# ── Internal params helpers ──

_DATAHUB_INTERNAL_KEY = "__datahub"


def strip_internal_params(params: dict[str, Any]) -> dict[str, Any]:
    """Remove __datahub internal key before sending to downloader/plugin."""
    if not params or _DATAHUB_INTERNAL_KEY not in params:
        return params
    cleaned = {k: v for k, v in params.items() if k != _DATAHUB_INTERNAL_KEY}
    return cleaned


def get_internal_retry_count(params: dict[str, Any]) -> int:
    """Read retry_count from __datahub internal params. Returns 0 if absent."""
    if not params:
        return 0
    internal = params.get(_DATAHUB_INTERNAL_KEY)
    if not isinstance(internal, dict):
        return 0
    return int(internal.get("retry_count", 0))


def bump_internal_retry_meta(
    params: dict[str, Any],
    reason: str,
    last_error: str | None = None,
) -> dict[str, Any]:
    """Increment retry_count and update retry metadata in __datahub.

    Returns a new params dict with updated __datahub.
    External __datahub is always overwritten (prevents user forgery).
    For retry_job, the params come from the DB (trusted), so retry_count
    increments correctly. For submit_command, __datahub is stripped first.
    """
    params = dict(params) if params else {}
    retry_count = get_internal_retry_count(params) + 1
    from src.datahub.core.time_utils import datahub_now_text
    params[_DATAHUB_INTERNAL_KEY] = {
        "retry_count": retry_count,
        "last_retry_at": datahub_now_text(),
        "last_retry_reason": reason,
        "last_error": last_error or "",
    }
    return params


class JobServiceError(Exception):
    """Raised when job submission fails due to validation or execution errors."""

    def __init__(self, error_code: str, message: str, ingestion_job_id: str | None = None):
        self.error_code = error_code
        self.message = message
        self.ingestion_job_id = ingestion_job_id
        super().__init__(message)


@dataclass
class JobResult:
    """Result of a job submission."""

    ingestion_job_id: str
    status: str
    downloader_job_id: str | None = None
    message: str | None = None
    original_job_id: str | None = None
    retry_of_job_id: str | None = None


class JobService:
    """Unified service for submitting and querying ingestion jobs."""

    def __init__(
        self,
        *,
        store: DataHubStore,
        plugins: list[PluginSpec],
        trigger_clients: dict[str, ExternalSyncClient],
        callback_base_url: str = "",
        callback_headers: dict[str, str] | None = None,
    ):
        self._store = store
        self._plugins = plugins
        self._trigger_clients = trigger_clients
        self._callback_base_url = callback_base_url
        self._callback_headers = callback_headers

    def submit_command(
        self,
        command_name: str,
        params: dict[str, Any] | None = None,
        source: str = "api",
        *,
        parent_job_id: str | None = None,
        retry_of_job_id: str | None = None,
    ) -> JobResult:
        """Submit a command for execution.

        Args:
            command_name: The command to trigger (e.g. "dcp_current_plan").
            params: Command parameters.
            source: Who triggered this job — one of cli/api/scheduler/ui_manual/retry.

        Returns:
            JobResult with ingestion_job_id and initial status.

        Raises:
            JobServiceError: On validation or execution failure.
        """
        if source not in VALID_SOURCES:
            raise JobServiceError("invalid_source", f"source must be one of {sorted(VALID_SOURCES)}, got '{source}'")

        params = params or {}
        # Strip any externally-provided __datahub to prevent forgery
        params = strip_internal_params(params)
        command = find_command(self._plugins, command_name)
        plugin = find_plugin_for_job(self._plugins, command_name)

        if command is None or plugin is None:
            # Check if command exists but is disabled
            for p in self._plugins:
                for c in p.commands:
                    if c.name == command_name and not c.enabled:
                        raise JobServiceError("command_disabled", f"command {command_name} is currently disabled")
            raise JobServiceError("unknown_command", f"command {command_name} not declared by any plugin")
        for param in command.required_params:
            if param not in params or params[param] is None:
                raise JobServiceError("missing_required_param", f"command {command_name} requires param {param}")

        ingestion_job_id = f"ing_{command_name}_{uuid4().hex[:12]}"
        producer_job_id = new_producer_job_id(command_name, params, command)
        trigger_type = command.trigger.get("type", "downloader_sync")

        # Plugin handler trigger
        if trigger_type == "plugin_handler":
            handler_path = command.trigger.get("handler")
            if not handler_path:
                raise JobServiceError("invalid_trigger", f"command {command_name} trigger has no handler")

            self._store.create_ingestion_job(
                ingestion_job_id=ingestion_job_id,
                producer_job_id=producer_job_id,
                job_type=command_name,
                params=params,
                plugin_id=plugin.name,
                source=source,
                parent_job_id=parent_job_id,
                retry_of_job_id=retry_of_job_id,
            )
            self._store.mark_job(ingestion_job_id, status="running")
            try:
                handler = load_plugin_handler(handler_path, plugin_name=plugin.name)
                ctx = build_handler_context(
                    store=self._store,
                    plugins=self._plugins,
                    trigger_clients=self._trigger_clients,
                    ingestion_job_id=ingestion_job_id,
                    callback_base_url=self._callback_base_url,
                    callback_headers=self._callback_headers,
                    params=params,
                    command=command,
                    plugin=plugin,
                )
                run_handler_async(handler, ctx)
            except Exception as exc:
                self._store.mark_job(ingestion_job_id, status="failed", error=str(exc))
                raise JobServiceError("plugin_handler_failed", str(exc), ingestion_job_id=ingestion_job_id) from exc

            return JobResult(
                ingestion_job_id=ingestion_job_id,
                status="running",
                message="plugin_handler started in background",
            )

        # Default: downloader_sync trigger
        self._store.create_ingestion_job(
            ingestion_job_id=ingestion_job_id,
            producer_job_id=producer_job_id,
            job_type=command_name,
            params=params,
            plugin_id=plugin.name,
            source=source,
            parent_job_id=parent_job_id,
            retry_of_job_id=retry_of_job_id,
        )

        client = self._trigger_clients.get(plugin.name)
        if client is None:
            self._store.mark_job(ingestion_job_id, status="failed", error="no external trigger connector configured")
            raise JobServiceError("no_connector", f"no connector configured for command {command_name}", ingestion_job_id=ingestion_job_id)

        downloader_job_type = command.trigger.get("job_type")
        if not downloader_job_type:
            self._store.mark_job(ingestion_job_id, status="failed", error="command trigger has no job_type")
            raise JobServiceError("invalid_trigger", f"command {command_name} trigger has no job_type", ingestion_job_id=ingestion_job_id)

        callback_url = f"{self._callback_base_url}/ingestion/v1/table-batches"
        try:
            response = client.sync(
                producer_job_id=producer_job_id,
                job_type=downloader_job_type,
                params=params,
                callback_url=callback_url,
                callback_headers=self._callback_headers,
            )
        except Exception as exc:
            self._store.mark_job(ingestion_job_id, status="failed", error=str(exc))
            raise JobServiceError("external_sync_failed", str(exc), ingestion_job_id=ingestion_job_id) from exc

        self._store.mark_job(ingestion_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
        return JobResult(
            ingestion_job_id=ingestion_job_id,
            status=response.get("status", "accepted"),
            downloader_job_id=producer_job_id,
        )

    def get_job_detail(self, ingestion_job_id: str) -> dict[str, Any] | None:
        """Get job detail by ingestion_job_id.

        Returns:
            Job dict or None if not found.
        """
        return self._store.get_job(ingestion_job_id)

    def retry_job(self, ingestion_job_id: str, *, source: str = "retry") -> JobResult:
        """Retry a failed job in-place using the same ingestion_job_id.

        Only jobs in a failed terminal state (failed / partial / cancelled) can be retried.
        The job is reopened with bumped __datahub.retry_count in params_json.
        No new ingestion_jobs row is created.

        Args:
            ingestion_job_id: The job ID to retry (same ID will be reused).
            source: Source label for the retry (default: "retry").

        Returns:
            JobResult with the same ingestion_job_id.

        Raises:
            JobServiceError: If the job is not found, has no command,
                is not in a retryable state, or is already running.
        """
        import json

        original = self._store.get_job(ingestion_job_id)
        if not original:
            raise JobServiceError("job_not_found", f"ingestion job {ingestion_job_id} not found")

        original_status = original.get("status", "")
        if original_status not in RETRYABLE_STATUSES:
            raise JobServiceError(
                "job_not_retryable",
                f"job {ingestion_job_id} has status '{original_status}', only {sorted(RETRYABLE_STATUSES)} can be retried",
            )

        command_name = original.get("trigger_key")
        if not command_name:
            raise JobServiceError("no_command", f"original job {ingestion_job_id} has no command")

        # Read and bump internal retry metadata
        params = json.loads(original.get("params_json") or "{}")
        last_error = original.get("error")
        params = bump_internal_retry_meta(params, reason="manual", last_error=last_error)

        # Reopen the same job row
        command = find_command(self._plugins, command_name)
        plugin = find_plugin_for_job(self._plugins, command_name)
        if command is None or plugin is None:
            raise JobServiceError("unknown_command", f"command {command_name} not found")

        producer_job_id = new_producer_job_id(command_name, params, command)
        reopened = self._store.reopen_job_for_retry(
            ingestion_job_id,
            new_downloader_job_id=producer_job_id,
            params_json=json.dumps(params, ensure_ascii=False),
            source=source,
        )

        # Concurrent protection: if reopen failed, another retry may have already started
        if not reopened:
            recheck = self._store.get_job(ingestion_job_id)
            if not recheck:
                raise JobServiceError("job_not_found", f"ingestion job {ingestion_job_id} not found")
            if recheck["status"] in ("triggering", "running", "accepted", "submitted"):
                raise JobServiceError(
                    "retry_already_started",
                    f"job {ingestion_job_id} is already {recheck['status']}, cannot retry again",
                    ingestion_job_id=ingestion_job_id,
                )
            raise JobServiceError(
                "job_not_retryable",
                f"job {ingestion_job_id} has status '{recheck['status']}', only {sorted(RETRYABLE_STATUSES)} can be retried",
                ingestion_job_id=ingestion_job_id,
            )

        # Trigger execution with stripped params
        trigger_type = command.trigger.get("type", "downloader_sync")
        business_params = strip_internal_params(params)

        if trigger_type == "plugin_handler":
            handler_path = command.trigger.get("handler")
            if not handler_path:
                self._store.mark_job(ingestion_job_id, status="failed", error="no handler")
                raise JobServiceError("invalid_trigger", f"command {command_name} trigger has no handler")

            self._store.mark_job(ingestion_job_id, status="running")
            try:
                handler = load_plugin_handler(handler_path, plugin_name=plugin.name)
                ctx = build_handler_context(
                    store=self._store,
                    plugins=self._plugins,
                    trigger_clients=self._trigger_clients,
                    ingestion_job_id=ingestion_job_id,
                    callback_base_url=self._callback_base_url,
                    callback_headers=self._callback_headers,
                    params=business_params,
                    command=command,
                    plugin=plugin,
                )
                run_handler_async(handler, ctx)
            except Exception as exc:
                self._store.mark_job(ingestion_job_id, status="failed", error=str(exc))
                raise JobServiceError("plugin_handler_failed", str(exc), ingestion_job_id=ingestion_job_id) from exc

            return JobResult(
                ingestion_job_id=ingestion_job_id,
                status="running",
                message="plugin_handler retry started in background",
            )

        # Default: downloader_sync trigger
        client = self._trigger_clients.get(plugin.name)
        if client is None:
            self._store.mark_job(ingestion_job_id, status="failed", error="no external trigger connector configured")
            raise JobServiceError("no_connector", f"no connector configured for command {command_name}", ingestion_job_id=ingestion_job_id)

        downloader_job_type = command.trigger.get("job_type")
        if not downloader_job_type:
            self._store.mark_job(ingestion_job_id, status="failed", error="command trigger has no job_type")
            raise JobServiceError("invalid_trigger", f"command {command_name} trigger has no job_type", ingestion_job_id=ingestion_job_id)

        callback_url = f"{self._callback_base_url}/ingestion/v1/table-batches"
        try:
            response = client.sync(
                producer_job_id=producer_job_id,
                job_type=downloader_job_type,
                params=business_params,
                callback_url=callback_url,
                callback_headers=self._callback_headers,
            )
        except Exception as exc:
            self._store.mark_job(ingestion_job_id, status="failed", error=str(exc))
            raise JobServiceError("external_sync_failed", str(exc), ingestion_job_id=ingestion_job_id) from exc

        self._store.mark_job(ingestion_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
        return JobResult(
            ingestion_job_id=ingestion_job_id,
            status=response.get("status", "accepted"),
            downloader_job_id=producer_job_id,
        )

    def retry_failed_children(
        self,
        parent_job_id: str,
        item_indexes: list[int] | None = None,
        *,
        source: str = "retry",
    ) -> dict[str, Any]:
        """Retry failed/skipped children of a fan-out parent job in-place.

        Each failed child job is reopened with the same ingestion_job_id.
        No new child jobs are created.

        Args:
            parent_job_id: The parent job ID with a fanout_run.
            item_indexes: Optional list of specific item indexes to retry.
                If None, all failed/skipped children are retried.
            source: Source label for retry jobs (default: "retry").

        Returns:
            Dict with parent_job_id, submitted count, skipped count, and item details.

        Raises:
            JobServiceError: If parent is not a fanout run or no failed children.
        """
        import json

        fanout_run = self._store.get_fanout_run(parent_job_id)
        if not fanout_run:
            raise JobServiceError("not_fanout_parent", f"job {parent_job_id} is not a fanout parent")

        failed_items = self._store.list_failed_fanout_items(parent_job_id, item_indexes=item_indexes)
        if not failed_items:
            raise JobServiceError("no_failed_children", f"no failed/skipped children found for fanout parent {parent_job_id}")

        child_command = fanout_run["child_command"]
        submitted = []
        skipped = []

        for item in failed_items:
            child_job_id = item.get("child_job_id")

            if child_job_id:
                child_job = self._store.get_job(child_job_id)
                if child_job and child_job["status"] not in RETRYABLE_STATUSES:
                    skipped.append({
                        "item_index": item["item_index"],
                        "child_job_id": child_job_id,
                        "reason": f"child status={child_job['status']}",
                    })
                    continue

                # In-place retry: reopen the same child job
                try:
                    params = json.loads(child_job.get("params_json") or "{}") if child_job else json.loads(item.get("params_json") or "{}")
                    last_error = child_job.get("error") if child_job else None
                    params = bump_internal_retry_meta(params, reason="manual", last_error=last_error)

                    command = find_command(self._plugins, child_command)
                    plugin = find_plugin_for_job(self._plugins, child_command)
                    if command is None or plugin is None:
                        skipped.append({
                            "item_index": item["item_index"],
                            "child_job_id": child_job_id,
                            "reason": f"command {child_command} not found",
                        })
                        continue

                    producer_job_id = new_producer_job_id(child_command, params, command)
                    self._store.reopen_job_for_retry(
                        child_job_id,
                        new_downloader_job_id=producer_job_id,
                        params_json=json.dumps(params, ensure_ascii=False),
                        source=source,
                    )

                    # Trigger execution with stripped params
                    business_params = strip_internal_params(params)
                    trigger_type = command.trigger.get("type", "downloader_sync")

                    if trigger_type == "plugin_handler":
                        self._store.mark_job(child_job_id, status="running")
                        handler_path = command.trigger.get("handler")
                        handler = load_plugin_handler(handler_path, plugin_name=plugin.name)
                        ctx = build_handler_context(
                            store=self._store,
                            plugins=self._plugins,
                            trigger_clients=self._trigger_clients,
                            ingestion_job_id=child_job_id,
                            callback_base_url=self._callback_base_url,
                            callback_headers=self._callback_headers,
                            params=business_params,
                            command=command,
                            plugin=plugin,
                        )
                        run_handler_async(handler, ctx)
                    else:
                        client = self._trigger_clients.get(plugin.name)
                        downloader_job_type = command.trigger.get("job_type")
                        if client and downloader_job_type:
                            callback_url = f"{self._callback_base_url}/ingestion/v1/table-batches"
                            try:
                                response = client.sync(
                                    producer_job_id=producer_job_id,
                                    job_type=downloader_job_type,
                                    params=business_params,
                                    callback_url=callback_url,
                                    callback_headers=self._callback_headers,
                                )
                                self._store.mark_job(child_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
                            except Exception as exc:
                                self._store.mark_job(child_job_id, status="failed", error=str(exc))
                        else:
                            self._store.mark_job(child_job_id, status="failed", error="no connector for child retry")

                    # Update fanout_item: reset to submitted, same child_job_id, increment retry_count
                    self._store.update_fanout_item_for_inplace_retry(item["id"])

                    submitted.append({
                        "item_index": item["item_index"],
                        "child_job_id": child_job_id,
                        "status": "submitted",
                    })
                except Exception as exc:
                    skipped.append({
                        "item_index": item["item_index"],
                        "child_job_id": child_job_id,
                        "reason": f"retry failed: {exc}",
                    })
            else:
                # No child_job_id yet — need to submit fresh
                params = json.loads(item.get("params_json") or "{}")
                try:
                    result = self.submit_command(
                        child_command,
                        params,
                        source=source,
                        parent_job_id=parent_job_id,
                    )
                    self._store.update_fanout_item_for_retry(item["id"], new_child_job_id=result.ingestion_job_id)
                    submitted.append({
                        "item_index": item["item_index"],
                        "child_job_id": result.ingestion_job_id,
                        "status": "submitted",
                    })
                except JobServiceError as exc:
                    skipped.append({
                        "item_index": item["item_index"],
                        "child_job_id": child_job_id,
                        "reason": f"submit failed: {exc.message}",
                    })

        # Only reopen if we actually submitted retries
        if len(submitted) > 0:
            if fanout_run["status"] in ("partial", "failed", "succeeded"):
                self._store.reopen_fanout_run(parent_job_id)
                self._store.reopen_parent_ingestion_job(parent_job_id)
        elif skipped:
            raise JobServiceError(
                "no_retry_submitted",
                f"0 of {len(failed_items)} items submitted, {len(skipped)} skipped: "
                + "; ".join(f"item {s['item_index']}: {s['reason']}" for s in skipped[:5]),
            )

        return {
            "parent_job_id": parent_job_id,
            "submitted": len(submitted),
            "skipped": len(skipped),
            "items": submitted,
            "skipped_items": skipped,
        }
