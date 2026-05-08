from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from storage.sqlite_store import SQLiteStore


def _parse_iso(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _duration_seconds(started_at: Any, finished_at: Any) -> float | None:
    started = _parse_iso(started_at)
    finished = _parse_iso(finished_at)
    if started is None or finished is None:
        return None
    return max(0.0, (finished - started).total_seconds())


def _job_group_health(
    rows: list[dict[str, Any]],
    *,
    group_key: str,
    running_timeout_hours: int,
) -> dict[str, Any]:
    counts = {"queued": 0, "running": 0, "succeeded": 0, "failed": 0}
    latest_by_group: dict[str, dict[str, Any]] = {}
    latest_failed: list[dict[str, Any]] = []
    active_running: list[dict[str, Any]] = []
    durations: list[float] = []
    latest_job: dict[str, Any] | None = None
    timeout_cutoff = datetime.now().astimezone() - timedelta(hours=running_timeout_hours)
    timed_out_running: list[dict[str, Any]] = []

    for row in rows:
        status = str(row.get("status") or "")
        if status in counts:
            counts[status] += 1
        group_value = str(row.get(group_key) or "")
        if group_value and group_value not in latest_by_group:
            latest_by_group[group_value] = row
        if status == "failed" and len(latest_failed) < 5:
            latest_failed.append(row)
        if status in {"queued", "running"}:
            active_running.append(row)
        duration = _duration_seconds(row.get("started_at"), row.get("finished_at"))
        if duration is not None:
            durations.append(duration)
        if latest_job is None:
            latest_job = row
        if status == "running":
            started_at = _parse_iso(row.get("started_at"))
            if started_at is not None and started_at <= timeout_cutoff:
                timed_out_running.append(row)

    return {
        "total": len(rows),
        "counts": counts,
        "latest_by_group": latest_by_group,
        "latest_failed_jobs": latest_failed,
        "active_running_jobs": active_running,
        "average_duration_seconds": (
            round(sum(durations) / len(durations), 2) if durations else None
        ),
        "latest_job": latest_job,
        "timed_out_running_jobs": timed_out_running,
    }


def get_job_health(
    store: SQLiteStore, running_timeout_hours: int = 6
) -> dict[str, Any]:
    conn = store._get_connection()
    try:
        external_rows = [
            store._deserialize_external_collection_job(row)
            for row in conn.execute(
                "SELECT * FROM external_collection_jobs ORDER BY created_at DESC"
            ).fetchall()
        ]
        external_rows = [row for row in external_rows if row is not None]

        processing_rows = [
            store._deserialize_processing_job(row)
            for row in conn.execute(
                "SELECT * FROM processing_jobs ORDER BY created_at DESC"
            ).fetchall()
        ]
        processing_rows = [row for row in processing_rows if row is not None]

        return {
            "external_collection_jobs": _job_group_health(
                external_rows,
                group_key="profile",
                running_timeout_hours=running_timeout_hours,
            ),
            "processing_jobs": _job_group_health(
                processing_rows,
                group_key="dataset_key",
                running_timeout_hours=running_timeout_hours,
            ),
        }
    finally:
        conn.close()

