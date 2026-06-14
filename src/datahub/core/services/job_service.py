"""Unified job service — single entry point for triggering and querying ingestion jobs.

All callers (CLI, API, future scheduler, future UI) should go through this service
instead of directly calling store / trigger_runtime / fan_out.
"""

from __future__ import annotations

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
        """Retry a failed job by re-creating it with the same command and params.

        Only jobs in a failed terminal state (failed / partial / cancelled) can be retried.

        Args:
            ingestion_job_id: The original failed job ID.
            source: Source label for the retry job (default: "retry").

        Returns:
            JobResult for the new retry job, with original_job_id and retry_of_job_id set.

        Raises:
            JobServiceError: If the original job is not found, has no command,
                is not in a retryable state, or an active retry already exists.
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

        # Check for active retry
        active_retry = self._store.find_active_retry(ingestion_job_id)
        if active_retry:
            raise JobServiceError(
                "retry_already_running",
                f"an active retry job {active_retry['ingestion_job_id']} (status={active_retry['status']}) already exists for {ingestion_job_id}",
            )

        command_name = original.get("trigger_key")
        if not command_name:
            raise JobServiceError("no_command", f"original job {ingestion_job_id} has no command")
        params = json.loads(original.get("params_json") or "{}")
        parent_job_id = original.get("parent_job_id")
        result = self.submit_command(
            command_name, params, source=source,
            parent_job_id=parent_job_id,
            retry_of_job_id=ingestion_job_id,
        )
        result.original_job_id = ingestion_job_id
        result.retry_of_job_id = ingestion_job_id
        return result

    def retry_failed_children(
        self,
        parent_job_id: str,
        item_indexes: list[int] | None = None,
        *,
        source: str = "retry",
    ) -> dict[str, Any]:
        """Retry failed/skipped children of a fan-out parent job.

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
            old_child_job_id = item.get("child_job_id")

            # Skip items with active child jobs
            if old_child_job_id:
                child_job = self._store.get_job(old_child_job_id)
                if child_job and child_job["status"] not in RETRYABLE_STATUSES:
                    skipped.append({
                        "item_index": item["item_index"],
                        "old_child_job_id": old_child_job_id,
                        "reason": f"child status={child_job['status']}",
                    })
                    continue

                # Check for active retry of this child
                active_retry = self._store.find_active_retry(old_child_job_id)
                if active_retry:
                    skipped.append({
                        "item_index": item["item_index"],
                        "old_child_job_id": old_child_job_id,
                        "reason": f"active retry {active_retry['ingestion_job_id']} already running",
                    })
                    continue

            # Submit new child job
            params = json.loads(item.get("params_json") or "{}")
            try:
                result = self.submit_command(
                    child_command,
                    params,
                    source=source,
                    parent_job_id=parent_job_id,
                    retry_of_job_id=old_child_job_id,
                )
                # Update fanout_item to point to new child
                self._store.update_fanout_item_for_retry(item["id"], new_child_job_id=result.ingestion_job_id)
                submitted.append({
                    "item_index": item["item_index"],
                    "old_child_job_id": old_child_job_id,
                    "new_child_job_id": result.ingestion_job_id,
                    "status": "submitted",
                })
            except JobServiceError as exc:
                skipped.append({
                    "item_index": item["item_index"],
                    "old_child_job_id": old_child_job_id,
                    "reason": f"submit failed: {exc.message}",
                })

        # Reopen fanout_run if it was closed
        if fanout_run["status"] in ("partial", "failed", "succeeded"):
            self._store.reopen_fanout_run(parent_job_id)
            # Mark parent job as running
            self._store.mark_job(parent_job_id, status="running", error=None)

        return {
            "parent_job_id": parent_job_id,
            "submitted": len(submitted),
            "skipped": len(skipped),
            "items": submitted,
            "skipped_items": skipped,
        }
