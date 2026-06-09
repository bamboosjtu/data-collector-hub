"""DCP plugin fan-out handlers.

Contains project fan-out and date-range fan-out logic specific to DCP.
These handlers are invoked by core's plugin_handler trigger mechanism.

Each handler receives a standard context dict and is responsible for:
- Querying source tables
- Creating child ingestion jobs
- Calling downloader via trigger_clients
- Recording success/failure per child job
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import date, datetime, timedelta
from typing import Any

from src.datahub.core.time_utils import datahub_current_year, datahub_days_ago, datahub_today, datahub_yesterday

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def resolve_auto_params(auto_params: dict[str, str], overrides: dict[str, Any] | None = None) -> dict[str, str]:
    """Resolve auto_params placeholders: yesterday, today, N_days_ago."""
    today = datahub_today()
    resolved: dict[str, str] = {}
    for key, value in auto_params.items():
        if overrides and key in overrides and overrides[key] is not None:
            resolved[key] = str(overrides[key])
        elif value == "today":
            resolved[key] = today.isoformat()
        elif value == "yesterday":
            resolved[key] = datahub_yesterday().isoformat()
        elif value.endswith("_days_ago"):
            try:
                n = int(value.split("_")[0])
                resolved[key] = datahub_days_ago(n).isoformat()
            except (ValueError, IndexError):
                resolved[key] = value
        else:
            resolved[key] = value
    return resolved


def _find_child_command_and_client(plugins, child_command_name, trigger_clients):
    """Helper to find child command spec, plugin, and client."""
    from src.datahub.core.plugin_loader import find_command, find_plugin_for_job

    child_command = find_command(plugins, child_command_name)
    child_plugin = find_plugin_for_job(plugins, child_command_name)
    if child_command is None or child_plugin is None:
        return None, None, None, f"child command {child_command_name} not found"

    client = trigger_clients.get(child_plugin.name)
    if client is None:
        return None, None, None, f"no connector for plugin {child_plugin.name}"

    downloader_job_type = child_command.trigger.get("job_type")
    if not downloader_job_type:
        return None, None, None, f"child command {child_command_name} has no job_type"

    return child_command, child_plugin, client, None


def _run_child_job(
    store, child_plugin, client, downloader_job_type,
    child_command_name, child_params, parent_job_id, callback_base_url,
    callback_headers=None,
):
    """Create and execute a single child ingestion job. Returns (job_id, status, error)."""
    from uuid import uuid4
    from src.datahub.core.trigger_runtime import new_producer_job_id
    from src.datahub.core.plugin_loader import find_command

    child_command = find_command([child_plugin], child_command_name)  # simplified
    child_job_id = f"ing_{child_command_name}_{uuid4().hex[:12]}"
    producer_job_id = new_producer_job_id(child_command_name, child_params, child_command)

    store.create_ingestion_job(
        ingestion_job_id=child_job_id,
        producer_job_id=producer_job_id,
        job_type=child_command_name,
        params=child_params,
        plugin_id=child_plugin.name,
        parent_job_id=parent_job_id,
    )

    try:
        callback_url = f"{callback_base_url}/ingestion/v1/table-batches"
        response = client.sync(
            producer_job_id=producer_job_id,
            job_type=downloader_job_type,
            params=child_params,
            callback_url=callback_url,
            callback_headers=callback_headers,
        )
        store.mark_job(child_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
        return child_job_id, response.get("status", "accepted"), None
    except Exception as exc:
        store.mark_job(child_job_id, status="failed", error=str(exc))
        return child_job_id, "failed", str(exc)


# ---------------------------------------------------------------------------
# Project fan-out handlers
# ---------------------------------------------------------------------------

def refresh_towers_for_current_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_projects for current year, trigger tower refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_towers_for_project",
        params_mapping={"prjCode": "projectCode"},
        cooldown_seconds=3.0,
    )


def refresh_substations_for_current_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_projects for current year, trigger substation refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_substations_for_project",
        params_mapping={"prjCode": "projectCode"},
        cooldown_seconds=3.0,
    )


def refresh_line_sections_for_current_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_projects for current year, trigger line section refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_line_sections_for_project",
        params_mapping={"prjCode": "projectCode"},
        cooldown_seconds=3.0,
    )


def _project_fan_out(
    *,
    ctx: dict[str, Any],
    child_command: str,
    params_mapping: dict[str, str],
    cooldown_seconds: float = 3.0,
) -> dict[str, Any]:
    """Generic project fan-out: query dcp_plan_projects for current year, trigger child per row.

    Includes consecutive failure circuit breaker: if N child jobs fail
    consecutively, the fan-out stops creating further children.
    """
    store = ctx["store"]
    plugins = ctx["plugins"]
    trigger_clients = ctx["trigger_clients"]
    parent_job_id = ctx["ingestion_job_id"]
    callback_base_url = ctx["callback_base_url"]
    params = ctx.get("params", {})

    # Allow cooldown_seconds override from params
    if "cooldown_seconds" in params:
        cooldown_seconds = float(params["cooldown_seconds"])

    # Circuit breaker threshold
    consecutive_failure_threshold = _DEFAULT_CONSECUTIVE_FAILURE_THRESHOLD
    if "consecutive_failure_threshold" in params:
        consecutive_failure_threshold = int(params["consecutive_failure_threshold"])

    # Parameter validation
    if cooldown_seconds < 0:
        error_msg = f"project_fan_out: cooldown_seconds must be >= 0, got {cooldown_seconds}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}
    if consecutive_failure_threshold < 1:
        error_msg = f"project_fan_out: consecutive_failure_threshold must be >= 1, got {consecutive_failure_threshold}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}
    max_items_param = params.get("max_items")
    if max_items_param is not None:
        max_items_param = int(max_items_param)
        if max_items_param < 1:
            error_msg = f"project_fan_out: max_items must be >= 1, got {max_items_param}"
            logger.error(error_msg)
            store.mark_job(parent_job_id, status="failed", error=error_msg)
            return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}

    # 1. Query dcp_plan_projects for current year
    current_year = datahub_current_year()
    rows = store.query_table("dcp_plan_projects", {"year": current_year}, limit=10000)
    if not rows:
        logger.warning("project fan-out %s: no rows in dcp_plan_projects for year=%s", child_command, current_year)
        store.mark_job(parent_job_id, status="succeeded", result={"total": 0, "succeeded": 0, "failed": 0, "items": []})
        return {"total": 0, "succeeded": 0, "failed": 0, "items": []}

    # 2. Extract unique projectCodes
    source_columns = list(params_mapping.keys())
    param_sets: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        child_params: dict[str, str] = {}
        for source_col in source_columns:
            target_param = params_mapping.get(source_col, source_col)
            value = row.get(source_col)
            if value is not None:
                child_params[target_param] = str(value)
        if child_params:
            key = "|".join(f"{k}={v}" for k, v in sorted(child_params.items()))
            if key not in seen:
                seen.add(key)
                param_sets.append(child_params)

    # Apply max_items limit
    max_items = max_items_param
    total_available = len(param_sets)
    if max_items is not None:
        param_sets = param_sets[:max_items]

    logger.info("project fan-out %s: %d projects (of %d available, circuit_breaker=%d)",
                child_command, len(param_sets), total_available, consecutive_failure_threshold)

    # Mark parent as running with fan_out_in_progress flag to prevent
    # _aggregate_parent_jobs from prematurely aggregating while we
    # are still creating children sequentially.
    store.mark_job(parent_job_id, status="running", result={"fan_out_in_progress": True, "total_available": total_available})

    # 3. Find child command
    child_cmd, child_plugin, client, error = _find_child_command_and_client(plugins, child_command, trigger_clients)
    if error:
        store.mark_job(parent_job_id, status="failed", error=error)
        return {"total": len(param_sets), "succeeded": 0, "failed": len(param_sets), "items": [], "error": error}

    downloader_job_type = child_cmd.trigger.get("job_type")

    # 4. Execute child jobs with circuit breaker
    callback_headers = ctx.get("callback_headers")
    results: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0
    consecutive_failures = 0
    circuit_opened = False
    first_failed_projectCode: str | None = None
    last_failed_projectCode: str | None = None
    skipped_remaining = 0

    for i, child_params in enumerate(param_sets):
        # Clean child params — remove fan-out control params
        clean_params = {k: v for k, v in child_params.items()
                        if k not in ("max_items", "max_concurrency", "cooldown_seconds", "consecutive_failure_threshold")}

        job_id, status, err = _run_child_job(
            store, child_plugin, client, downloader_job_type,
            child_command, clean_params, parent_job_id, callback_base_url,
            callback_headers=callback_headers,
        )

        # If _run_child_job itself failed (exception), count as immediate failure
        if err:
            failed += 1
            consecutive_failures += 1
            project_code = clean_params.get("projectCode", f"project_{i}")
            if first_failed_projectCode is None:
                first_failed_projectCode = project_code
            last_failed_projectCode = project_code
            results.append({"params": clean_params, "ingestion_job_id": job_id, "status": status, "failed": True})
            logger.warning("project fan-out [%d/%d] %s FAILED: %s (consecutive=%d/%d)",
                           i + 1, len(param_sets), clean_params, err,
                           consecutive_failures, consecutive_failure_threshold)
        else:
            # Wait for child to reach terminal state
            child_job = _wait_for_child_terminal(store, job_id)
            child_failed = _is_child_failed(child_job)

            if child_failed:
                failed += 1
                consecutive_failures += 1
                project_code = clean_params.get("projectCode", f"project_{i}")
                if first_failed_projectCode is None:
                    first_failed_projectCode = project_code
                last_failed_projectCode = project_code
                child_status = child_job.get("status", "unknown") if child_job else "unknown"
                results.append({"params": clean_params, "ingestion_job_id": job_id, "status": child_status, "failed": True})
                logger.warning("project fan-out [%d/%d] %s child FAILED (consecutive=%d/%d)",
                               i + 1, len(param_sets), clean_params,
                               consecutive_failures, consecutive_failure_threshold)
            else:
                succeeded += 1
                consecutive_failures = 0  # Reset on success
                child_status = child_job.get("status", "unknown") if child_job else "unknown"
                results.append({"params": clean_params, "ingestion_job_id": job_id, "status": child_status, "failed": False})
                logger.info("project fan-out [%d/%d] %s -> %s",
                            i + 1, len(param_sets), clean_params, child_status)

        # Circuit breaker check
        if consecutive_failures >= consecutive_failure_threshold:
            skipped_remaining = len(param_sets) - i - 1
            circuit_opened = True
            logger.error("project fan-out CIRCUIT BREAKER: %d consecutive failures reached threshold %d, "
                         "skipping remaining %d projects",
                         consecutive_failures, consecutive_failure_threshold, skipped_remaining)
            break

        if i < len(param_sets) - 1 and cooldown_seconds > 0:
            time.sleep(cooldown_seconds)

    # 5. Build summary
    summary: dict[str, Any] = {
        "total_available": total_available,
        "created_children": len(results),
        "succeeded_children": succeeded,
        "failed_children": failed,
        "items": results,
    }

    if circuit_opened:
        summary["skipped_remaining_projects"] = skipped_remaining
        summary["first_failed_projectCode"] = first_failed_projectCode
        summary["last_failed_projectCode"] = last_failed_projectCode
        summary["consecutive_failure_threshold"] = consecutive_failure_threshold
        circuit_error = (f"circuit breaker opened: {consecutive_failures} consecutive project child jobs failed")
        store.mark_job(parent_job_id, status="failed", error=circuit_error, result=summary)
        logger.error("project fan-out parent %s FAILED: %s", parent_job_id, circuit_error)
    else:
        # Mark parent as running — _aggregate_parent_jobs will set final status
        # once all children reach terminal state
        store.mark_job(parent_job_id, status="running", result=summary)

    return summary


# ---------------------------------------------------------------------------
# Date-range fan-out handlers
# ---------------------------------------------------------------------------

# Terminal statuses for child jobs
_TERMINAL_STATUSES = frozenset({"succeeded", "partial", "failed", "cancelled"})

# Default circuit breaker threshold for consecutive child failures
_DEFAULT_CONSECUTIVE_FAILURE_THRESHOLD = 5

# How long to wait between polls when waiting for a child to reach terminal state
_CHILD_POLL_INTERVAL_SECONDS = 5

# Maximum time to wait for a single child job to reach terminal state
_CHILD_POLL_TIMEOUT_SECONDS = 1800  # 30 minutes


def _is_child_failed(job: dict[str, Any] | None) -> bool:
    """Determine if a child job in terminal state represents a failure.

    A child is considered failed if:
    - status is failed or cancelled
    - error is non-empty
    - producer_status contains request_failed
    - producer_status contains planning failed / fetch failed (project domain)
    - partial with no data and no indication of legitimate completion

    A child is NOT considered failed if:
    - status is succeeded (even with row_count=0 — some projects have no data)
    - current_message indicates "all tasks already completed" or "all messages delivered"
    """
    if job is None:
        return True

    status = job.get("status", "")
    if status in ("failed", "cancelled"):
        return True

    error = job.get("error")
    if error:
        return True

    # Check producer_status_json for failure indicators
    producer_status_str = str(job.get("producer_status_json") or "")
    if "request_failed" in producer_status_str:
        return True
    if "planning failed" in producer_status_str:
        return True
    if "fetch failed" in producer_status_str:
        return True

    # Check result_json for failure indicators
    result_str = str(job.get("result_json") or "")
    if "request_failed" in result_str:
        return True
    if "planning failed" in result_str:
        return True
    if "fetch failed" in result_str:
        return True

    # partial with no data — check if it's a legitimate empty result
    if status == "partial":
        row_count = job.get("row_count") or 0
        message_received = job.get("message_received") or 0
        # If current_message indicates legitimate completion, not a failure
        current_msg = str(job.get("current_message") or "")
        if "all tasks already completed" in current_msg or "all messages delivered" in current_msg:
            return False
        if row_count == 0 and message_received == 0:
            return True

    return False


def _wait_for_child_terminal(
    store: Any,
    child_job_id: str,
    *,
    poll_interval: float = _CHILD_POLL_INTERVAL_SECONDS,
    timeout: float = _CHILD_POLL_TIMEOUT_SECONDS,
) -> dict[str, Any] | None:
    """Wait for a child job to reach terminal state. Returns the job dict or None on timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = store.get_job(child_job_id)
        if job and job.get("status") in _TERMINAL_STATUSES:
            return job
        time.sleep(poll_interval)
    # Timeout — return whatever we have
    return store.get_job(child_job_id)


def backfill_daily_meetings_by_range(ctx: dict[str, Any]) -> dict[str, Any]:
    """Date-range fan-out: split date range into chunks, trigger daily meeting refresh per chunk."""
    return _date_range_fan_out(
        ctx=ctx,
        child_command="refresh_daily_meetings_by_range",
        start_date_param="startDate",
        end_date_param="endDate",
        chunk_days=7,
        cooldown_seconds=2.0,
    )


def _date_range_fan_out(
    *,
    ctx: dict[str, Any],
    child_command: str,
    start_date_param: str = "startDate",
    end_date_param: str = "endDate",
    chunk_days: int = 7,
    cooldown_seconds: float = 2.0,
    date_format: str = "%Y-%m-%d",
) -> dict[str, Any]:
    """Generic date-range fan-out: split date range, trigger child per chunk.

    Includes consecutive failure circuit breaker: if N child jobs fail
    consecutively, the fan-out stops creating further children.
    """
    store = ctx["store"]
    plugins = ctx["plugins"]
    trigger_clients = ctx["trigger_clients"]
    parent_job_id = ctx["ingestion_job_id"]
    callback_base_url = ctx["callback_base_url"]
    params = ctx.get("params", {})

    # Allow chunk_days override from params
    if "chunk_days" in params:
        chunk_days = int(params["chunk_days"])

    # Allow cooldown_seconds override from params
    if "cooldown_seconds" in params:
        cooldown_seconds = float(params["cooldown_seconds"])

    # Circuit breaker threshold
    consecutive_failure_threshold = _DEFAULT_CONSECUTIVE_FAILURE_THRESHOLD
    if "consecutive_failure_threshold" in params:
        consecutive_failure_threshold = int(params["consecutive_failure_threshold"])

    # Parameter validation
    if chunk_days < 1:
        error_msg = f"date_range_fan_out: chunk_days must be >= 1, got {chunk_days}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}
    if cooldown_seconds < 0:
        error_msg = f"date_range_fan_out: cooldown_seconds must be >= 0, got {cooldown_seconds}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}
    if consecutive_failure_threshold < 1:
        error_msg = f"date_range_fan_out: consecutive_failure_threshold must be >= 1, got {consecutive_failure_threshold}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}

    # 1. Parse dates
    start_str = params.get(start_date_param)
    end_str = params.get(end_date_param)
    if not start_str or not end_str:
        error_msg = f"date_range_fan_out requires {start_date_param} and {end_date_param}"
        logger.error(error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}

    start_date = datetime.strptime(str(start_str), date_format).date()
    end_date = datetime.strptime(str(end_str), date_format).date()

    # 2. Generate chunks
    chunks: list[tuple[date, date]] = []
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)

    logger.info("date_range_fan_out %s: %d chunks from %s to %s (chunk_days=%d, circuit_breaker=%d)",
                child_command, len(chunks), start_date, end_date, chunk_days, consecutive_failure_threshold)

    # Mark parent as running with fan_out_in_progress flag to prevent
    # _aggregate_parent_jobs from prematurely aggregating while we
    # are still creating children sequentially.
    store.mark_job(parent_job_id, status="running", result={"fan_out_in_progress": True, "total_chunks": len(chunks)})

    # 3. Find child command
    child_cmd, child_plugin, client, error = _find_child_command_and_client(plugins, child_command, trigger_clients)
    if error:
        store.mark_job(parent_job_id, status="failed", error=error)
        return {"total": len(chunks), "succeeded": 0, "failed": len(chunks), "items": [], "error": error}

    downloader_job_type = child_cmd.trigger.get("job_type")

    # 4. Execute child jobs with circuit breaker
    callback_headers = ctx.get("callback_headers")
    results: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0
    consecutive_failures = 0
    circuit_opened = False
    first_failed_date: str | None = None
    last_failed_date: str | None = None
    skipped_remaining = 0

    for i, (chunk_start, chunk_end) in enumerate(chunks):
        child_params = dict(params)
        child_params[start_date_param] = chunk_start.strftime(date_format)
        child_params[end_date_param] = chunk_end.strftime(date_format)
        # Remove fan-out control params — must not be passed to downloader child
        child_params.pop("chunk_days", None)
        child_params.pop("cooldown_seconds", None)
        child_params.pop("consecutive_failure_threshold", None)
        child_params.pop("max_concurrency", None)

        job_id, status, err = _run_child_job(
            store, child_plugin, client, downloader_job_type,
            child_command, child_params, parent_job_id, callback_base_url,
            callback_headers=callback_headers,
        )

        # If _run_child_job itself failed (exception), count as immediate failure
        if err:
            failed += 1
            consecutive_failures += 1
            chunk_date_str = chunk_start.strftime(date_format)
            if first_failed_date is None:
                first_failed_date = chunk_date_str
            last_failed_date = chunk_date_str
            results.append({"params": child_params, "ingestion_job_id": job_id, "status": status, "failed": True})
            logger.warning("date_range_fan_out [%d/%d] %s~%s FAILED: %s (consecutive=%d/%d)",
                           i + 1, len(chunks), chunk_start, chunk_end, err,
                           consecutive_failures, consecutive_failure_threshold)
        else:
            # Wait for child to reach terminal state
            child_job = _wait_for_child_terminal(store, job_id)
            child_failed = _is_child_failed(child_job)

            if child_failed:
                failed += 1
                consecutive_failures += 1
                chunk_date_str = chunk_start.strftime(date_format)
                if first_failed_date is None:
                    first_failed_date = chunk_date_str
                last_failed_date = chunk_date_str
                child_status = child_job.get("status", "unknown") if child_job else "unknown"
                results.append({"params": child_params, "ingestion_job_id": job_id, "status": child_status, "failed": True})
                logger.warning("date_range_fan_out [%d/%d] %s~%s child FAILED (consecutive=%d/%d)",
                               i + 1, len(chunks), chunk_start, chunk_end,
                               consecutive_failures, consecutive_failure_threshold)
            else:
                succeeded += 1
                consecutive_failures = 0  # Reset on success
                child_status = child_job.get("status", "unknown") if child_job else "unknown"
                results.append({"params": child_params, "ingestion_job_id": job_id, "status": child_status, "failed": False})
                logger.info("date_range_fan_out [%d/%d] %s~%s -> %s",
                            i + 1, len(chunks), chunk_start, chunk_end, child_status)

        # Circuit breaker check
        if consecutive_failures >= consecutive_failure_threshold:
            skipped_remaining = len(chunks) - i - 1
            circuit_opened = True
            logger.error("date_range_fan_out CIRCUIT BREAKER: %d consecutive failures reached threshold %d, "
                         "skipping remaining %d chunks",
                         consecutive_failures, consecutive_failure_threshold, skipped_remaining)
            break

        if i < len(chunks) - 1 and cooldown_seconds > 0:
            time.sleep(cooldown_seconds)

    # 5. Build summary
    summary: dict[str, Any] = {
        "total": len(chunks),
        "created_children": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "date_range": f"{start_date}~{end_date}",
        "chunk_days": chunk_days,
        "items": results,
    }

    if circuit_opened:
        summary["skipped_remaining_dates"] = skipped_remaining
        summary["first_failed_date"] = first_failed_date
        summary["last_failed_date"] = last_failed_date
        summary["consecutive_failure_threshold"] = consecutive_failure_threshold
        circuit_error = (f"circuit breaker opened: {consecutive_failures} consecutive child jobs failed "
                         f"for {downloader_job_type}")
        store.mark_job(parent_job_id, status="failed", error=circuit_error, result=summary)
        logger.error("date_range_fan_out parent %s FAILED: %s", parent_job_id, circuit_error)
    else:
        # Mark parent as running — _aggregate_parent_jobs will set final status
        # once all children reach terminal state
        store.mark_job(parent_job_id, status="running", result=summary)

    return summary


# ---------------------------------------------------------------------------
# Yesterday incremental handler
# ---------------------------------------------------------------------------

def refresh_daily_meetings_yesterday(ctx: dict[str, Any]) -> dict[str, Any]:
    """Resolve yesterday's date and trigger a single daily_meeting_range job."""
    store = ctx["store"]
    plugins = ctx["plugins"]
    trigger_clients = ctx["trigger_clients"]
    parent_job_id = ctx["ingestion_job_id"]
    callback_base_url = ctx["callback_base_url"]

    yesterday = datahub_yesterday().isoformat()
    child_params = {"startDate": yesterday, "endDate": yesterday}

    # Find child command
    child_cmd, child_plugin, client, error = _find_child_command_and_client(
        plugins, "refresh_daily_meetings_by_range", trigger_clients,
    )
    if error:
        store.mark_job(parent_job_id, status="failed", error=error)
        return {"total": 1, "succeeded": 0, "failed": 1, "items": [], "error": error}

    downloader_job_type = child_cmd.trigger.get("job_type")

    job_id, status, err = _run_child_job(
        store, child_plugin, client, downloader_job_type,
        "refresh_daily_meetings_by_range", child_params, parent_job_id, callback_base_url,
        callback_headers=ctx.get("callback_headers"),
    )

    result = {"total": 1, "succeeded": 0 if err else 1, "failed": 1 if err else 0,
              "items": [{"params": child_params, "ingestion_job_id": job_id, "status": status}]}
    store.mark_job(parent_job_id, status="succeeded" if not err else "failed", result=result)
    return result
