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

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def resolve_auto_params(auto_params: dict[str, str], overrides: dict[str, Any] | None = None) -> dict[str, str]:
    """Resolve auto_params placeholders: yesterday, today, N_days_ago."""
    today = date.today()
    resolved: dict[str, str] = {}
    for key, value in auto_params.items():
        if overrides and key in overrides and overrides[key] is not None:
            resolved[key] = str(overrides[key])
        elif value == "today":
            resolved[key] = today.isoformat()
        elif value == "yesterday":
            resolved[key] = (today - timedelta(days=1)).isoformat()
        elif value.endswith("_days_ago"):
            try:
                n = int(value.split("_")[0])
                resolved[key] = (today - timedelta(days=n)).isoformat()
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
    """Generic project fan-out: query dcp_plan_projects for current year, trigger child per row."""
    store = ctx["store"]
    plugins = ctx["plugins"]
    trigger_clients = ctx["trigger_clients"]
    parent_job_id = ctx["ingestion_job_id"]
    callback_base_url = ctx["callback_base_url"]
    params = ctx.get("params", {})

    # 1. Query dcp_plan_projects for current year
    current_year = str(datetime.now().year)
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
    max_items = params.get("max_items")
    total_available = len(param_sets)
    if max_items is not None:
        max_items = int(max_items)
        param_sets = param_sets[:max_items]

    logger.info("project fan-out %s: %d projects (of %d available)", child_command, len(param_sets), total_available)

    # 3. Find child command
    child_cmd, child_plugin, client, error = _find_child_command_and_client(plugins, child_command, trigger_clients)
    if error:
        store.mark_job(parent_job_id, status="failed", error=error)
        return {"total": len(param_sets), "succeeded": 0, "failed": len(param_sets), "items": [], "error": error}

    downloader_job_type = child_cmd.trigger.get("job_type")

    # 4. Execute child jobs
    callback_headers = ctx.get("callback_headers")
    results: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0

    for i, child_params in enumerate(param_sets):
        job_id, status, err = _run_child_job(
            store, child_plugin, client, downloader_job_type,
            child_command, child_params, parent_job_id, callback_base_url,
            callback_headers=callback_headers,
        )
        results.append({"params": child_params, "ingestion_job_id": job_id, "status": status})
        if err:
            failed += 1
            logger.warning("project fan-out [%d/%d] %s FAILED: %s", i + 1, len(param_sets), child_params, err)
        else:
            succeeded += 1
            logger.info("project fan-out [%d/%d] %s -> %s", i + 1, len(param_sets), child_params, status)

        if i < len(param_sets) - 1 and cooldown_seconds > 0:
            time.sleep(cooldown_seconds)

    summary = {"total": len(param_sets), "total_available": total_available, "succeeded": succeeded, "failed": failed, "items": results}
    # Mark parent as running — _aggregate_parent_jobs will set final status
    # once all children reach terminal state
    store.mark_job(parent_job_id, status="running", result=summary)
    return summary


# ---------------------------------------------------------------------------
# Date-range fan-out handlers
# ---------------------------------------------------------------------------

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
    """Generic date-range fan-out: split date range, trigger child per chunk."""
    store = ctx["store"]
    plugins = ctx["plugins"]
    trigger_clients = ctx["trigger_clients"]
    parent_job_id = ctx["ingestion_job_id"]
    callback_base_url = ctx["callback_base_url"]
    params = ctx.get("params", {})

    # Allow chunk_days override from params
    if "chunk_days" in params:
        chunk_days = int(params["chunk_days"])

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

    logger.info("date_range_fan_out %s: %d chunks from %s to %s (chunk_days=%d)",
                child_command, len(chunks), start_date, end_date, chunk_days)

    # 3. Find child command
    child_cmd, child_plugin, client, error = _find_child_command_and_client(plugins, child_command, trigger_clients)
    if error:
        store.mark_job(parent_job_id, status="failed", error=error)
        return {"total": len(chunks), "succeeded": 0, "failed": len(chunks), "items": [], "error": error}

    downloader_job_type = child_cmd.trigger.get("job_type")

    # 4. Execute child jobs
    callback_headers = ctx.get("callback_headers")
    results: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0

    for i, (chunk_start, chunk_end) in enumerate(chunks):
        child_params = dict(params)
        child_params[start_date_param] = chunk_start.strftime(date_format)
        child_params[end_date_param] = chunk_end.strftime(date_format)
        child_params.pop("chunk_days", None)

        job_id, status, err = _run_child_job(
            store, child_plugin, client, downloader_job_type,
            child_command, child_params, parent_job_id, callback_base_url,
            callback_headers=callback_headers,
        )
        results.append({"params": child_params, "ingestion_job_id": job_id, "status": status})
        if err:
            failed += 1
            logger.warning("date_range_fan_out [%d/%d] %s~%s FAILED: %s", i + 1, len(chunks), chunk_start, chunk_end, err)
        else:
            succeeded += 1
            logger.info("date_range_fan_out [%d/%d] %s~%s -> %s", i + 1, len(chunks), chunk_start, chunk_end, status)

        if i < len(chunks) - 1 and cooldown_seconds > 0:
            time.sleep(cooldown_seconds)

    summary = {"total": len(chunks), "succeeded": succeeded, "failed": failed,
               "date_range": f"{start_date}~{end_date}", "chunk_days": chunk_days, "items": results}
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

    yesterday = (date.today() - timedelta(days=1)).isoformat()
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
