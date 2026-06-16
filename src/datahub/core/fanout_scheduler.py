"""Fan-out scheduler: advances running fanout_runs by submitting child jobs.

Each tick:
1. Claim running fanout_run leases
2. Recover stale submitting items
3. Sync submitted child terminal states from ingestion_jobs
4. Compute stats and consecutive failures
5. Circuit-break: skip pending items if threshold reached
6. Submit new child jobs within capacity and cooldown
7. Close fanout_run when all items are terminal
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.datahub.core.time_utils import datahub_now, datahub_now_text

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = frozenset({"succeeded", "partial", "failed", "cancelled"})

_TRANSIENT_KEYWORDS = (
    "session_expired",
    "recoverable",
    "sgcc client is expired",
    "dcp_client_expired",
    "timeout",
    "etimedout",
    "econnreset",
    "slot_unavailable",
    "runner_timeout",
)

_MAX_TRANSIENT_RETRIES = 2


def _is_transient_child_failure(child_job: dict[str, Any]) -> bool:
    """Check if a failed child job is a transient/recoverable failure."""
    texts: list[str] = []
    for key in ("error", "producer_status_json", "result_json"):
        val = child_job.get(key)
        if val:
            texts.append(str(val))
    combined = " ".join(texts).lower()
    return any(kw in combined for kw in _TRANSIENT_KEYWORDS)


def _is_child_non_success(child_job: dict[str, Any]) -> bool:
    """Check if a child job is in a non-success terminal state (failed/partial/cancelled)."""
    return child_job.get("status") in ("failed", "partial", "cancelled")


def _get_child_retry_count(child_job: dict[str, Any]) -> int:
    """Read retry_count from child job's __datahub internal params."""
    import json
    try:
        params = json.loads(child_job.get("params_json") or "{}")
        internal = params.get("__datahub")
        if isinstance(internal, dict):
            return int(internal.get("retry_count", 0))
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return 0


def start_fanout_scheduler(
    store,
    trigger_clients,
    plugins,
    *,
    callback_base_url: str,
    callback_headers: dict[str, str] | None,
    tick_interval: float = 3.0,
) -> threading.Event:
    """Start the fan-out scheduler background thread. Returns a shutdown Event."""
    scheduler_id = f"hub-{os.getpid()}-{uuid4().hex[:8]}"
    shutdown = threading.Event()

    def loop():
        while not shutdown.is_set():
            try:
                fanout_scheduler_tick(
                    store,
                    trigger_clients,
                    plugins,
                    callback_base_url=callback_base_url,
                    callback_headers=callback_headers,
                    scheduler_id=scheduler_id,
                )
            except Exception as exc:
                logger.error("fanout scheduler tick error: %s", exc, exc_info=True)
            shutdown.wait(tick_interval)

    thread = threading.Thread(target=loop, name="hub-fanout-scheduler", daemon=True)
    thread.start()
    return shutdown


def fanout_scheduler_tick(
    store,
    trigger_clients,
    plugins,
    *,
    callback_base_url: str,
    callback_headers: dict[str, str] | None,
    scheduler_id: str,
) -> None:
    """Advance all running fanout_runs."""
    runs = store.get_running_fanout_runs(limit=50)
    for run in runs:
        try:
            _advance_fanout_run(
                store,
                trigger_clients,
                plugins,
                run,
                callback_base_url=callback_base_url,
                callback_headers=callback_headers,
                scheduler_id=scheduler_id,
            )
        except Exception as exc:
            logger.error("fanout scheduler error for %s: %s", run["parent_job_id"], exc, exc_info=True)


def _inplace_retry_child(
    store, trigger_clients, plugins, run, item, child_job,
    *,
    callback_base_url: str,
    callback_headers: dict[str, str] | None,
) -> None:
    """In-place retry a failed child job: reopen same job_id, bump __datahub, re-trigger."""
    import json
    from src.datahub.core.services.job_service import (
        bump_internal_retry_meta,
        strip_internal_params,
    )
    from src.datahub.core.plugin_loader import find_command, find_plugin_for_job
    from src.datahub.core.trigger_runtime import new_producer_job_id

    child_job_id = item["child_job_id"]
    child_command = run["child_command"]
    command = find_command(plugins, child_command)
    plugin = find_plugin_for_job(plugins, child_command)

    if command is None or plugin is None:
        store.update_fanout_item_terminal(item["id"], status="failed", error=f"child command not found: {child_command}")
        return

    params = json.loads(child_job.get("params_json") or "{}")
    last_error = child_job.get("error")
    params = bump_internal_retry_meta(params, reason="auto_non_success", last_error=last_error)

    producer_job_id = new_producer_job_id(child_command, params, command)
    store.reopen_job_for_retry(
        child_job_id,
        new_producer_job_id=producer_job_id,
        params_json=json.dumps(params, ensure_ascii=False),
        source="retry",
    )

    business_params = strip_internal_params(params)
    trigger_type = command.trigger.get("type", "downloader_sync")

    if trigger_type == "plugin_handler":
        from src.datahub.core.fan_out import build_handler_context, load_plugin_handler, run_handler_async
        store.mark_job(child_job_id, status="running")
        handler_path = command.trigger.get("handler")
        handler = load_plugin_handler(handler_path, plugin_name=plugin.name)
        ctx = build_handler_context(
            store=store,
            plugins=plugins,
            trigger_clients=trigger_clients,
            ingestion_job_id=child_job_id,
            callback_base_url=callback_base_url,
            callback_headers=callback_headers,
            params=business_params,
            command=command,
            plugin=plugin,
        )
        run_handler_async(handler, ctx)
    else:
        client = trigger_clients.get(plugin.name)
        downloader_job_type = command.trigger.get("job_type")
        if client and downloader_job_type:
            callback_url = f"{callback_base_url}/ingestion/v1/table-batches"
            try:
                response = client.sync(
                    producer_job_id=producer_job_id,
                    job_type=downloader_job_type,
                    params=business_params,
                    callback_url=callback_url,
                    callback_headers=callback_headers,
                )
                store.mark_job(child_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
            except Exception as exc:
                store.mark_job(child_job_id, status="failed", error=str(exc))
        else:
            store.mark_job(child_job_id, status="failed", error="no connector for auto-retry")

    # Update fanout_item: same child_job_id, increment retry_count, clear error
    store.update_fanout_item_for_inplace_retry(item["id"])


def _advance_fanout_run(
    store,
    trigger_clients,
    plugins,
    run,
    *,
    callback_base_url: str,
    callback_headers: dict[str, str] | None,
    scheduler_id: str,
) -> None:
    parent_job_id = run["parent_job_id"]

    # Claim lease
    if not store.claim_fanout_run(parent_job_id, scheduler_id, lease_seconds=30):
        return

    # 1. Recover stale submitting items
    reset_count = store.reset_stale_submitting_items(parent_job_id, stale_seconds=120)
    if reset_count:
        logger.info("fanout %s: reset %d stale submitting items", parent_job_id, reset_count)

    # 2. Sync submitted child terminal states from ingestion_jobs
    for item in store.list_submitted_fanout_items(parent_job_id):
        child_job = store.get_job(item["child_job_id"])
        if child_job and child_job["status"] in _TERMINAL_STATUSES:
            from plugins.dcp.fan_out import _is_child_failed
            failed = _is_child_failed(child_job)
            if failed:
                child_retry_count = _get_child_retry_count(child_job)

                # Transient failure: retry with backoff (up to _MAX_TRANSIENT_RETRIES)
                if _is_transient_child_failure(child_job) and item.get("retry_count", 0) < _MAX_TRANSIENT_RETRIES:
                    retry_count = item.get("retry_count", 0)
                    delay_seconds = 3 * (2 ** retry_count)
                    error_summary = (child_job.get("error") or "transient failure")[:200]
                    logger.info(
                        "fanout %s: transient child failure, retrying item %s after %ds "
                        "(retry_count=%d, child_job_id=%s, error=%s)",
                        parent_job_id, item["id"], delay_seconds,
                        retry_count, item["child_job_id"], error_summary,
                    )
                    store.retry_fanout_item(
                        item["id"],
                        error=child_job.get("error") or "transient failure",
                        delay_seconds=delay_seconds,
                    )
                # Non-success auto-retry: in-place retry once (retry_count < 1)
                elif _is_child_non_success(child_job) and child_retry_count < 1:
                    logger.info(
                        "fanout %s: auto-retrying child %s in-place (child_retry_count=%d, status=%s)",
                        parent_job_id, item["child_job_id"], child_retry_count, child_job["status"],
                    )
                    _inplace_retry_child(store, trigger_clients, plugins, run, item, child_job,
                                         callback_base_url=callback_base_url,
                                         callback_headers=callback_headers)
                else:
                    store.update_fanout_item_terminal(
                        item["id"],
                        status="failed",
                        error=child_job.get("error"),
                    )
            else:
                store.update_fanout_item_terminal(
                    item["id"],
                    status="succeeded",
                )

    # 3. Compute stats and consecutive failures
    stats = store.get_fanout_stats(parent_job_id)
    consecutive_failures = store.get_consecutive_failures(parent_job_id)
    store.update_fanout_run_consecutive(parent_job_id, consecutive_failures)

    # 4. Circuit breaker
    run = store.get_fanout_run(parent_job_id)
    if not run["circuit_opened"] and consecutive_failures >= run["consecutive_failure_threshold"]:
        logger.error("fanout %s: circuit breaker opened after %d consecutive failures (threshold=%d)",
                     parent_job_id, consecutive_failures, run["consecutive_failure_threshold"])
        store.mark_fanout_circuit_open(parent_job_id)
        store.skip_pending_fanout_items(parent_job_id)
        stats = store.get_fanout_stats(parent_job_id)
        run = store.get_fanout_run(parent_job_id)

    # 5. Close if no pending/submitting/submitted work remains
    if stats["pending"] == 0 and stats["submitting"] == 0 and stats["submitted"] == 0:
        _close_fanout_parent(store, parent_job_id, stats, run)
        return

    # 6. If circuit is open, wait for submitted items to drain
    run = store.get_fanout_run(parent_job_id)
    if run["circuit_opened"]:
        return

    # 7. Submit new child jobs within capacity and cooldown
    capacity = run["max_concurrency"] - stats["submitted"] - stats["submitting"]
    while capacity > 0:
        if not _cooldown_elapsed(run["last_submit_at"], run["cooldown_seconds"]):
            break

        item = store.claim_next_pending_fanout_item(parent_job_id, scheduler_id)
        if item is None:
            break

        try:
            _submit_claimed_item(
                store,
                trigger_clients,
                plugins,
                run,
                item,
                callback_base_url=callback_base_url,
                callback_headers=callback_headers,
            )
        except Exception as exc:
            logger.exception("fanout %s: submit item %s failed", parent_job_id, item.get("id"))
            store.update_fanout_item_terminal(item["id"], status="failed", error=str(exc))
        store.update_fanout_run_submit(parent_job_id, datahub_now_text())
        run = store.get_fanout_run(parent_job_id)
        capacity -= 1


def _cooldown_elapsed(last_submit_at: str | None, cooldown_seconds: float) -> bool:
    """Check if enough time has elapsed since last submission.

    Both stored timestamps and datahub_now() are Beijing time text.
    strptime produces a naive datetime; compare as naive to avoid tz mismatch.
    """
    if not last_submit_at or cooldown_seconds <= 0:
        return True
    try:
        last_dt = datetime.strptime(last_submit_at, "%Y-%m-%d %H:%M:%S")
        # Use naive now (same Beijing time, just without tzinfo) for comparison
        now_naive = datetime.strptime(datahub_now_text(), "%Y-%m-%d %H:%M:%S")
        elapsed = (now_naive - last_dt).total_seconds()
        return elapsed >= cooldown_seconds
    except (ValueError, TypeError):
        return True


def _submit_claimed_item(
    store,
    trigger_clients,
    plugins,
    run,
    item,
    *,
    callback_base_url: str,
    callback_headers: dict[str, str] | None,
) -> None:
    """Submit a claimed fanout_item as a child job."""
    from plugins.dcp.fan_out import _run_child_job
    from src.datahub.core.plugin_loader import find_command, find_plugin_for_job

    child_command = run["child_command"]
    child_cmd = find_command(plugins, child_command)
    child_plugin = find_plugin_for_job(plugins, child_command)

    if child_cmd is None or child_plugin is None:
        store.update_fanout_item_terminal(item["id"], status="failed", error=f"child command not found: {child_command}")
        return

    client = trigger_clients.get(child_plugin.name)
    downloader_job_type = child_cmd.trigger.get("job_type")
    if client is None or not downloader_job_type:
        store.update_fanout_item_terminal(item["id"], status="failed", error=f"child connector/job_type missing: {child_command}")
        return

    params = json.loads(item["params_json"])
    child_job_id, child_status, err = _run_child_job(
        store,
        child_plugin,
        client,
        downloader_job_type,
        child_command,
        params,
        run["parent_job_id"],
        callback_base_url,
        callback_headers=callback_headers,
    )

    if err:
        store.update_fanout_item_terminal(item["id"], status="failed", child_job_id=child_job_id, error=err)
    else:
        store.update_fanout_item_submitted(item["id"], child_job_id=child_job_id)


def _close_fanout_parent(store, parent_job_id: str, stats: dict[str, int], run: dict[str, Any]) -> None:
    """Close a fanout_run and mark the parent ingestion_job."""
    succeeded = stats.get("succeeded", 0)
    failed = stats.get("failed", 0)
    skipped = stats.get("skipped", 0)

    # Determine parent status
    if succeeded > 0 and failed == 0 and skipped == 0:
        parent_status = "succeeded"
        run_status = "succeeded"
    elif succeeded > 0:
        parent_status = "partial"
        run_status = "partial"
    else:
        parent_status = "failed"
        run_status = "failed"

    result = {
        "total": run["total"],
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "circuit_opened": bool(run["circuit_opened"]),
        "consecutive_failure_threshold": run["consecutive_failure_threshold"],
        "max_concurrency": run["max_concurrency"],
    }

    error_msg = None
    if run["circuit_opened"]:
        error_msg = f"circuit breaker opened: {run['consecutive_failure_threshold']} consecutive failures"
    elif failed > 0 and succeeded == 0:
        error_msg = f"all {failed} child jobs failed"

    store.close_fanout_run(parent_job_id, status=run_status, result=result)
    store.mark_job(parent_job_id, status=parent_status, result=result, error=error_msg)

    logger.info("fanout %s closed: %s (succeeded=%d, failed=%d, skipped=%d)",
                parent_job_id, run_status, succeeded, failed, skipped)
