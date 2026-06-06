"""Generic fan-out runners for commands that iterate over query results or date ranges.

Fan-out types:
  - fan_out: query a source table, trigger child command for each row
  - date_range_fan_out: split a date range into chunks, trigger child command per chunk

Both are configured entirely through plugin.yaml — no DCP-specific logic here.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from .specs import CommandSpec, PluginSpec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Auto-params resolution (yesterday, today, N_days_ago, etc.)
# ---------------------------------------------------------------------------

def resolve_auto_params(auto_params: dict[str, str], overrides: dict[str, Any] | None = None) -> dict[str, str]:
    """Resolve auto_params placeholders like 'yesterday', 'today', 'N_days_ago'.

    Overrides dict can provide explicit values that take precedence.
    """
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


# ---------------------------------------------------------------------------
# Fan-out (query-based)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FanOutConfig:
    """Parsed fan-out configuration from a command's trigger dict."""

    source_table: str
    source_filters: dict[str, str]
    source_columns: list[str]
    child_command: str
    params_mapping: dict[str, str]
    max_concurrency: int = 1
    cooldown_seconds: float = 3.0

    @classmethod
    def from_trigger(cls, trigger: dict[str, Any]) -> FanOutConfig:
        sq = trigger.get("source_query") or {}
        return cls(
            source_table=str(sq.get("table", "")),
            source_filters=dict(sq.get("filters") or {}),
            source_columns=list(sq.get("columns") or []),
            child_command=str(trigger.get("child_command", "")),
            params_mapping=dict(trigger.get("params_mapping") or {}),
            max_concurrency=int(trigger.get("max_concurrency", 1)),
            cooldown_seconds=float(trigger.get("cooldown_seconds", 3.0)),
        )


def resolve_source_filters(
    filters: dict[str, str],
) -> dict[str, Any]:
    """Resolve special filter values like 'current' for year."""
    resolved: dict[str, Any] = {}
    now = datetime.now()
    for key, value in filters.items():
        if value == "current":
            resolved[key] = str(now.year)
        else:
            resolved[key] = value
    return resolved


def execute_fan_out(
    *,
    fan_out_config: FanOutConfig,
    store: Any,  # DataHubStore
    plugins: list[PluginSpec],
    trigger_clients: dict[str, Any],  # dict[str, ExternalSyncClient]
    parent_job_id: str,
    callback_base_url: str,
    max_items: int | None = None,
) -> dict[str, Any]:
    """Execute a fan-out command: query source, trigger child command for each row.

    Returns a summary dict with total, succeeded, failed counts.
    """
    from .plugin_loader import find_command, find_plugin_for_job
    from .trigger_runtime import ExternalSyncClient, new_producer_job_id

    # 1. Resolve filters
    resolved_filters = resolve_source_filters(fan_out_config.source_filters)

    # 2. Query source table
    rows = store.query_table(
        fan_out_config.source_table,
        resolved_filters,
        limit=10000,
    )
    if not rows:
        logger.warning("fan-out %s: no rows found in %s with filters %s",
                       fan_out_config.child_command, fan_out_config.source_table, resolved_filters)
        return {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0, "items": []}

    # 3. Extract param values from rows
    columns = fan_out_config.source_columns or list(fan_out_config.params_mapping.keys())
    param_sets: list[dict[str, str]] = []
    for row in rows:
        child_params: dict[str, str] = {}
        for source_col in columns:
            target_param = fan_out_config.params_mapping.get(source_col, source_col)
            value = row.get(source_col)
            if value is not None:
                child_params[target_param] = str(value)
        if child_params:
            param_sets.append(child_params)

    # Deduplicate by params dict
    seen: set[str] = set()
    unique_params: list[dict[str, str]] = []
    for p in param_sets:
        key = "|".join(f"{k}={v}" for k, v in sorted(p.items()))
        if key not in seen:
            seen.add(key)
            unique_params.append(p)

    # Apply max_items limit
    total_available = len(unique_params)
    if max_items is not None and max_items > 0:
        unique_params = unique_params[:max_items]

    logger.info("fan-out %s: %d unique param sets (of %d available), max_items=%s",
                fan_out_config.child_command, len(unique_params), total_available, max_items)

    # 4. Find child command and plugin
    child_command = find_command(plugins, fan_out_config.child_command)
    child_plugin = find_plugin_for_job(plugins, fan_out_config.child_command)
    if child_command is None or child_plugin is None:
        logger.error("fan-out: child command %s not found", fan_out_config.child_command)
        return {"total": len(unique_params), "succeeded": 0, "failed": len(unique_params),
                "skipped": 0, "items": [], "error": f"child command {fan_out_config.child_command} not found"}

    client = trigger_clients.get(child_plugin.name)
    if client is None:
        logger.error("fan-out: no connector for plugin %s", child_plugin.name)
        return {"total": len(unique_params), "succeeded": 0, "failed": len(unique_params),
                "skipped": 0, "items": [], "error": f"no connector for plugin {child_plugin.name}"}

    downloader_job_type = child_command.trigger.get("job_type")
    if not downloader_job_type:
        logger.error("fan-out: child command %s has no job_type", fan_out_config.child_command)
        return {"total": len(unique_params), "succeeded": 0, "failed": len(unique_params),
                "skipped": 0, "items": [], "error": f"child command {fan_out_config.child_command} has no job_type"}

    # 5. Execute child commands (serial, with cooldown)
    results: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0

    for i, child_params in enumerate(unique_params):
        from uuid import uuid4

        child_job_id = f"ing_{fan_out_config.child_command}_{uuid4().hex[:12]}"
        producer_job_id = new_producer_job_id(fan_out_config.child_command, child_params, child_command)

        # Create ingestion job record
        store.create_ingestion_job(
            ingestion_job_id=child_job_id,
            producer_job_id=producer_job_id,
            job_type=fan_out_config.child_command,
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
            )
            store.mark_job(child_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
            results.append({
                "params": child_params,
                "ingestion_job_id": child_job_id,
                "downloader_job_id": producer_job_id,
                "status": response.get("status", "accepted"),
            })
            succeeded += 1
            logger.info("fan-out [%d/%d] %s params=%s -> %s",
                        i + 1, len(unique_params), fan_out_config.child_command, child_params, response.get("status"))
        except Exception as exc:
            store.mark_job(child_job_id, status="failed", error=str(exc))
            results.append({
                "params": child_params,
                "ingestion_job_id": child_job_id,
                "status": "failed",
                "error": str(exc),
            })
            failed += 1
            logger.warning("fan-out [%d/%d] %s params=%s -> FAILED: %s",
                           i + 1, len(unique_params), fan_out_config.child_command, child_params, exc)

        # Cooldown between requests
        if i < len(unique_params) - 1 and fan_out_config.cooldown_seconds > 0:
            time.sleep(fan_out_config.cooldown_seconds)

    summary = {
        "total": len(unique_params),
        "total_available": total_available,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": 0,
        "items": results,
    }

    # Update parent job with fan-out result
    store.mark_job(parent_job_id, status="succeeded" if failed == 0 else "partial", result=summary)

    return summary


def execute_fan_out_async(
    *,
    fan_out_config: FanOutConfig,
    store: Any,
    plugins: list[PluginSpec],
    trigger_clients: dict[str, Any],
    parent_job_id: str,
    callback_base_url: str,
    max_items: int | None = None,
) -> None:
    """Run fan-out in a background thread. Returns immediately after starting."""
    def _run():
        try:
            execute_fan_out(
                fan_out_config=fan_out_config,
                store=store,
                plugins=plugins,
                trigger_clients=trigger_clients,
                parent_job_id=parent_job_id,
                callback_base_url=callback_base_url,
                max_items=max_items,
            )
        except Exception as exc:
            logger.exception("fan-out async execution failed: %s", exc)
            try:
                store.mark_job(parent_job_id, status="failed", error=str(exc))
            except Exception:
                pass

    thread = threading.Thread(target=_run, daemon=True, name=f"fan-out-{parent_job_id}")
    thread.start()


# ---------------------------------------------------------------------------
# Date-range fan-out
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DateRangeFanOutConfig:
    """Parsed date_range_fan_out configuration from a command's trigger dict."""

    child_command: str
    start_date_param: str
    end_date_param: str
    chunk_days: int = 7
    fallback_chunk_days: int = 1
    cooldown_seconds: float = 2.0
    date_format: str = "%Y-%m-%d"

    @classmethod
    def from_trigger(cls, trigger: dict[str, Any]) -> DateRangeFanOutConfig:
        return cls(
            child_command=str(trigger.get("child_command", "")),
            start_date_param=str(trigger.get("start_date_param", "startDate")),
            end_date_param=str(trigger.get("end_date_param", "endDate")),
            chunk_days=int(trigger.get("chunk_days", 7)),
            fallback_chunk_days=int(trigger.get("fallback_chunk_days", 1)),
            cooldown_seconds=float(trigger.get("cooldown_seconds", 2.0)),
            date_format=str(trigger.get("date_format", "%Y-%m-%d")),
        )


def generate_date_chunks(
    start_date: date,
    end_date: date,
    chunk_days: int,
) -> list[tuple[date, date]]:
    """Split a date range into chunks of chunk_days."""
    chunks: list[tuple[date, date]] = []
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)
    return chunks


def execute_date_range_fan_out(
    *,
    config: DateRangeFanOutConfig,
    params: dict[str, Any],
    store: Any,
    plugins: list[PluginSpec],
    trigger_clients: dict[str, Any],
    parent_job_id: str,
    callback_base_url: str,
) -> dict[str, Any]:
    """Execute a date_range_fan_out: split date range, trigger child command per chunk."""
    from .plugin_loader import find_command, find_plugin_for_job
    from .trigger_runtime import new_producer_job_id

    # 1. Parse start/end dates from params
    start_str = params.get(config.start_date_param)
    end_str = params.get(config.end_date_param)
    if not start_str or not end_str:
        error_msg = f"date_range_fan_out requires {config.start_date_param} and {config.end_date_param}"
        logger.error(error_msg)
        return {"total": 0, "succeeded": 0, "failed": 0, "items": [], "error": error_msg}

    start_date = datetime.strptime(str(start_str), config.date_format).date()
    end_date = datetime.strptime(str(end_str), config.date_format).date()

    # 2. Generate date chunks
    chunks = generate_date_chunks(start_date, end_date, config.chunk_days)
    logger.info("date_range_fan_out %s: %d chunks from %s to %s (chunk_days=%d)",
                config.child_command, len(chunks), start_date, end_date, config.chunk_days)

    # 3. Find child command and plugin
    child_command = find_command(plugins, config.child_command)
    child_plugin = find_plugin_for_job(plugins, config.child_command)
    if child_command is None or child_plugin is None:
        error_msg = f"child command {config.child_command} not found"
        logger.error("date_range_fan_out: %s", error_msg)
        return {"total": len(chunks), "succeeded": 0, "failed": len(chunks), "items": [], "error": error_msg}

    client = trigger_clients.get(child_plugin.name)
    if client is None:
        error_msg = f"no connector for plugin {child_plugin.name}"
        logger.error("date_range_fan_out: %s", error_msg)
        return {"total": len(chunks), "succeeded": 0, "failed": len(chunks), "items": [], "error": error_msg}

    downloader_job_type = child_command.trigger.get("job_type")
    if not downloader_job_type:
        error_msg = f"child command {config.child_command} has no job_type"
        logger.error("date_range_fan_out: %s", error_msg)
        return {"total": len(chunks), "succeeded": 0, "failed": len(chunks), "items": [], "error": error_msg}

    # 4. Execute child commands per chunk
    results: list[dict[str, Any]] = []
    succeeded = 0
    failed = 0

    for i, (chunk_start, chunk_end) in enumerate(chunks):
        from uuid import uuid4

        child_params = dict(params)
        child_params[config.start_date_param] = chunk_start.strftime(config.date_format)
        child_params[config.end_date_param] = chunk_end.strftime(config.date_format)
        # Remove fan-out specific params from child params
        child_params.pop("chunk_days", None)

        child_job_id = f"ing_{config.child_command}_{uuid4().hex[:12]}"
        producer_job_id = new_producer_job_id(config.child_command, child_params, child_command)

        store.create_ingestion_job(
            ingestion_job_id=child_job_id,
            producer_job_id=producer_job_id,
            job_type=config.child_command,
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
            )
            store.mark_job(child_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
            results.append({
                "params": child_params,
                "ingestion_job_id": child_job_id,
                "status": response.get("status", "accepted"),
            })
            succeeded += 1
            logger.info("date_range_fan_out [%d/%d] %s %s~%s -> %s",
                        i + 1, len(chunks), config.child_command, chunk_start, chunk_end, response.get("status"))
        except Exception as exc:
            store.mark_job(child_job_id, status="failed", error=str(exc))
            results.append({
                "params": child_params,
                "ingestion_job_id": child_job_id,
                "status": "failed",
                "error": str(exc),
            })
            failed += 1
            logger.warning("date_range_fan_out [%d/%d] %s %s~%s -> FAILED: %s",
                           i + 1, len(chunks), config.child_command, chunk_start, chunk_end, exc)

        # Cooldown between requests
        if i < len(chunks) - 1 and config.cooldown_seconds > 0:
            time.sleep(config.cooldown_seconds)

    summary = {
        "total": len(chunks),
        "succeeded": succeeded,
        "failed": failed,
        "date_range": f"{start_date}~{end_date}",
        "chunk_days": config.chunk_days,
        "items": results,
    }

    store.mark_job(parent_job_id, status="succeeded" if failed == 0 else "partial", result=summary)
    return summary


def execute_date_range_fan_out_async(
    *,
    config: DateRangeFanOutConfig,
    params: dict[str, Any],
    store: Any,
    plugins: list[PluginSpec],
    trigger_clients: dict[str, Any],
    parent_job_id: str,
    callback_base_url: str,
) -> None:
    """Run date_range_fan_out in a background thread."""
    def _run():
        try:
            execute_date_range_fan_out(
                config=config,
                params=params,
                store=store,
                plugins=plugins,
                trigger_clients=trigger_clients,
                parent_job_id=parent_job_id,
                callback_base_url=callback_base_url,
            )
        except Exception as exc:
            logger.exception("date_range_fan_out async execution failed: %s", exc)
            try:
                store.mark_job(parent_job_id, status="failed", error=str(exc))
            except Exception:
                pass

    thread = threading.Thread(target=_run, daemon=True, name=f"dr-fanout-{parent_job_id}")
    thread.start()
