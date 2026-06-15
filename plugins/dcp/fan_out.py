"""DCP plugin fan-out handlers.

Contains project fan-out and date-range fan-out logic specific to DCP.
These handlers are invoked by core's plugin_handler trigger mechanism.

Each handler receives a standard context dict and is responsible for:
- Querying source tables or parsing date ranges
- Creating fanout_runs / fanout_items in SQLite
- Returning immediately — the scheduler tick advances execution
"""

from __future__ import annotations

import logging
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


def _resolve_concurrency(command_spec, params) -> int:
    """Resolve max_concurrency from command spec and user params."""
    default = command_spec.max_concurrency
    limit = command_spec.max_concurrency_limit or default
    requested = int(params.get("max_concurrency", default))
    actual = max(1, min(requested, limit))
    if requested > limit:
        logger.warning("max_concurrency=%d exceeds limit=%d, capped", requested, limit)
    return actual


def _resolve_cooldown(command_spec, params, default: float = 3.0) -> float:
    """Resolve cooldown_seconds from command spec, params, or default."""
    spec_val = command_spec.cooldown_seconds
    param_val = params.get("cooldown_seconds")
    if param_val is not None:
        return max(0.0, float(param_val))
    if spec_val > 0:
        return spec_val
    return default


def _resolve_failure_threshold(params, default: int = 5) -> int:
    """Resolve consecutive_failure_threshold from params or default."""
    val = params.get("consecutive_failure_threshold")
    if val is not None:
        return max(1, int(val))
    return default


# ---------------------------------------------------------------------------
# Project fan-out handlers
# ---------------------------------------------------------------------------

def refresh_towers_for_current_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_year_project for current year, trigger tower refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_towers_for_project",
        params_mapping={"prjCode": "projectCode"},
    )


def refresh_substations_for_current_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_year_project for current year, trigger substation refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_substations_for_project",
        params_mapping={"prjCode": "projectCode"},
    )


def refresh_line_sections_for_current_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_year_project for current year, trigger line section refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_line_sections_for_project",
        params_mapping={"prjCode": "projectCode"},
    )


def refresh_towers_for_all_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_year_project for specified years, trigger tower refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_towers_for_project",
        params_mapping={"prjCode": "projectCode"},
        multi_year=True,
    )


def refresh_substations_for_all_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_year_project for specified years, trigger substation refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_substations_for_project",
        params_mapping={"prjCode": "projectCode"},
        multi_year=True,
    )


def refresh_line_sections_for_all_plan_projects(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan-out: query dcp_plan_year_project for specified years, trigger line section refresh per projectCode."""
    return _project_fan_out(
        ctx=ctx,
        child_command="refresh_line_sections_for_project",
        params_mapping={"prjCode": "projectCode"},
        multi_year=True,
    )


def _project_fan_out(
    *,
    ctx: dict[str, Any],
    child_command: str,
    params_mapping: dict[str, str],
    multi_year: bool = False,
) -> dict[str, Any]:
    """Generic project fan-out: query dcp_plan_year_project, create fanout_run.

    When multi_year=False (default): queries current year only.
    When multi_year=True: queries years from params.years (list of ints),
      falling back to [current_year] if not specified.

    Handler returns immediately — scheduler tick advances execution.
    """
    store = ctx["store"]
    parent_job_id = ctx["ingestion_job_id"]
    parent_command = ctx["command"].name
    plugin_id = ctx["plugin"].name
    params = ctx.get("params", {})

    max_concurrency = _resolve_concurrency(ctx["command"], params)
    cooldown_seconds = _resolve_cooldown(ctx["command"], params, default=3.0)
    consecutive_failure_threshold = _resolve_failure_threshold(params)

    # Parameter validation
    if cooldown_seconds < 0:
        error_msg = f"project_fan_out: cooldown_seconds must be >= 0, got {cooldown_seconds}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}
    if consecutive_failure_threshold < 1:
        error_msg = f"project_fan_out: consecutive_failure_threshold must be >= 1, got {consecutive_failure_threshold}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}

    max_items_param = params.get("max_items")
    if max_items_param is not None:
        max_items_param = int(max_items_param)
        if max_items_param < 1:
            error_msg = f"project_fan_out: max_items must be >= 1, got {max_items_param}"
            logger.error(error_msg)
            store.mark_job(parent_job_id, status="failed", error=error_msg)
            return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}

    # 1. Determine years to query
    if multi_year:
        years_param = params.get("years")
        if years_param:
            years = [str(y) for y in years_param]
        else:
            years = [datahub_current_year()]
    else:
        years = [datahub_current_year()]

    # 2. Query dcp_plan_year_project for each year
    all_rows: list[dict[str, Any]] = []
    for year in years:
        rows = store.query_table("dcp_plan_year_project", {"year": year}, limit=10000)
        all_rows.extend(rows)

    if not all_rows:
        logger.warning("project fan-out %s: no rows in dcp_plan_year_project for years=%s", child_command, years)
        store.mark_job(parent_job_id, status="succeeded", result={"total": 0, "succeeded": 0, "failed": 0})
        return {"total": 0, "succeeded": 0, "failed": 0}

    # 3. Extract unique projectCodes
    source_columns = list(params_mapping.keys())
    param_sets: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in all_rows:
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
                # Clean fan-out control params
                clean = {k: v for k, v in child_params.items()
                         if k not in ("max_items", "max_concurrency", "cooldown_seconds", "consecutive_failure_threshold", "years")}
                param_sets.append(clean)

    # Apply max_items limit
    total_available = len(param_sets)
    if max_items_param is not None:
        param_sets = param_sets[:max_items_param]

    if not param_sets:
        store.mark_job(parent_job_id, status="succeeded", result={"total": 0, "succeeded": 0, "failed": 0})
        return {"total": 0, "succeeded": 0, "failed": 0}

    logger.info("project fan-out %s: %d projects (of %d available, years=%s, max_concurrency=%d, circuit_breaker=%d)",
                child_command, len(param_sets), total_available, years, max_concurrency, consecutive_failure_threshold)

    # 3. Create fanout_run + fanout_items (single transaction)
    store.create_fanout_run_with_items(
        parent_job_id=parent_job_id,
        plugin_id=plugin_id,
        parent_command=parent_command,
        child_command=child_command,
        param_sets=param_sets,
        max_concurrency=max_concurrency,
        cooldown_seconds=cooldown_seconds,
        consecutive_failure_threshold=consecutive_failure_threshold,
    )

    store.mark_job(
        parent_job_id,
        status="running",
        result={"fanout_scheduler": True, "total": len(param_sets), "total_available": total_available, "max_concurrency": max_concurrency},
    )

    return {"status": "running", "total": len(param_sets), "total_available": total_available, "max_concurrency": max_concurrency}


# ---------------------------------------------------------------------------
# Date-range fan-out handlers
# ---------------------------------------------------------------------------

# Terminal statuses for child jobs
_TERMINAL_STATUSES = frozenset({"succeeded", "partial", "failed", "cancelled"})

# Default circuit breaker threshold for consecutive child failures
_DEFAULT_CONSECUTIVE_FAILURE_THRESHOLD = 5


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


def backfill_daily_meetings_by_range(ctx: dict[str, Any]) -> dict[str, Any]:
    """Date-range fan-out: split date range into chunks, create fanout_run."""
    return _date_range_fan_out(
        ctx=ctx,
        child_command="refresh_daily_meetings_by_range",
        start_date_param="startDate",
        end_date_param="endDate",
        chunk_days=7,
    )


def _date_range_fan_out(
    *,
    ctx: dict[str, Any],
    child_command: str,
    start_date_param: str = "startDate",
    end_date_param: str = "endDate",
    chunk_days: int = 7,
    date_format: str = "%Y-%m-%d",
) -> dict[str, Any]:
    """Generic date-range fan-out: split date range, create fanout_run.

    Handler returns immediately — scheduler tick advances execution.
    """
    store = ctx["store"]
    parent_job_id = ctx["ingestion_job_id"]
    parent_command = ctx["command"].name
    plugin_id = ctx["plugin"].name
    params = ctx.get("params", {})

    # Allow chunk_days override from params
    if "chunk_days" in params:
        chunk_days = int(params["chunk_days"])

    max_concurrency = _resolve_concurrency(ctx["command"], params)
    cooldown_seconds = _resolve_cooldown(ctx["command"], params, default=2.0)
    consecutive_failure_threshold = _resolve_failure_threshold(params)

    # Parameter validation
    if chunk_days < 1:
        error_msg = f"date_range_fan_out: chunk_days must be >= 1, got {chunk_days}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}
    if cooldown_seconds < 0:
        error_msg = f"date_range_fan_out: cooldown_seconds must be >= 0, got {cooldown_seconds}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}
    if consecutive_failure_threshold < 1:
        error_msg = f"date_range_fan_out: consecutive_failure_threshold must be >= 1, got {consecutive_failure_threshold}"
        logger.error(error_msg)
        store.mark_job(parent_job_id, status="failed", error=error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}

    # 1. Parse dates
    start_str = params.get(start_date_param)
    end_str = params.get(end_date_param)
    if not start_str or not end_str:
        error_msg = f"date_range_fan_out requires {start_date_param} and {end_date_param}"
        logger.error(error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "error": error_msg}

    start_date = datetime.strptime(str(start_str), date_format).date()
    end_date = datetime.strptime(str(end_str), date_format).date()

    # 2. Generate chunks
    chunks: list[tuple[date, date]] = []
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)

    if not chunks:
        store.mark_job(parent_job_id, status="succeeded", result={"total": 0, "succeeded": 0, "failed": 0})
        return {"total": 0, "succeeded": 0, "failed": 0}

    logger.info("date_range_fan_out %s: %d chunks from %s to %s (chunk_days=%d, max_concurrency=%d, circuit_breaker=%d)",
                child_command, len(chunks), start_date, end_date, chunk_days, max_concurrency, consecutive_failure_threshold)

    # 3. Build param_sets for each chunk
    param_sets: list[dict[str, str]] = []
    for chunk_start, chunk_end in chunks:
        child_params = dict(params)
        child_params[start_date_param] = chunk_start.strftime(date_format)
        child_params[end_date_param] = chunk_end.strftime(date_format)
        # Remove fan-out control params — must not be passed to downloader child
        child_params.pop("chunk_days", None)
        child_params.pop("cooldown_seconds", None)
        child_params.pop("consecutive_failure_threshold", None)
        child_params.pop("max_concurrency", None)
        child_params.pop("max_items", None)
        param_sets.append(child_params)

    # 4. Create fanout_run + fanout_items (single transaction)
    store.create_fanout_run_with_items(
        parent_job_id=parent_job_id,
        plugin_id=plugin_id,
        parent_command=parent_command,
        child_command=child_command,
        param_sets=param_sets,
        max_concurrency=max_concurrency,
        cooldown_seconds=cooldown_seconds,
        consecutive_failure_threshold=consecutive_failure_threshold,
    )

    store.mark_job(
        parent_job_id,
        status="running",
        result={"fanout_scheduler": True, "total": len(param_sets), "date_range": f"{start_date}~{end_date}",
                "chunk_days": chunk_days, "max_concurrency": max_concurrency},
    )

    return {"status": "running", "total": len(param_sets), "date_range": f"{start_date}~{end_date}",
            "chunk_days": chunk_days, "max_concurrency": max_concurrency}


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
        return {"total": 1, "succeeded": 0, "failed": 1, "error": error}

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
