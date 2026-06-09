from __future__ import annotations

import json
from typing import Any
from urllib import request
from uuid import uuid4

from .specs import CommandSpec, ConnectorSpec
from .time_utils import datahub_now_text


class ExternalSyncClient:
    def __init__(self, connector: ConnectorSpec):
        self.connector = connector
        self.base_url = connector.base_url.rstrip("/")
        self.timeout_seconds = connector.timeout_seconds

    def sync(self, *, producer_job_id: str, job_type: str, params: dict[str, Any], callback_url: str, callback_headers: dict[str, str] | None = None, debug: bool = False) -> dict[str, Any]:
        sink: dict[str, Any] = {"type": "http_callback", "url": callback_url}
        if callback_headers:
            sink["headers"] = callback_headers
        return self._json(
            "/sync",
            "POST",
            {
                "downloader_job_id": producer_job_id,
                "job_type": job_type,
                "params": params,
                "sink": sink,
                "debug": debug,
            },
        )

    def get_job_status(self, producer_job_id: str) -> dict[str, Any] | None:
        """Poll downloader for job status. Returns status dict or None if not found."""
        try:
            return self._json(f"/sync/jobs/{producer_job_id}", "GET")
        except Exception:
            return None

    def _json(self, path: str, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(f"{self.base_url}{path}", data=data, method=method, headers={"Content-Type": "application/json"})
        opener = request.build_opener(request.ProxyHandler({}))
        with opener.open(req, timeout=self.timeout_seconds) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}


def new_producer_job_id(command_name: str, params: dict[str, Any], command: CommandSpec | None = None) -> str:
    suffix = None
    if command:
        for param in command.required_params:
            if params.get(param):
                suffix = str(params[param])
                break
    if not suffix:
        suffix = uuid4().hex[:12]
    safe_suffix = suffix.replace(":", "_").replace("/", "_").replace("\\", "_")
    return f"job_{command_name}_{safe_suffix}_{uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Downloader job status poller
# ---------------------------------------------------------------------------

import logging

logger = logging.getLogger(__name__)

# Map downloader status -> Hub status
_DOWNLOADER_STATUS_MAP = {
    "accepted": "accepted",
    "running": "running",
    "delivering": "delivering",
    "succeeded": "succeeded",
    "partial": "partial",
    "failed": "failed",
    "cancelled": "cancelled",
}

# Terminal states — no further polling needed
_TERMINAL_STATUSES = frozenset({"succeeded", "partial", "failed", "cancelled"})

# Default stale threshold: 30 minutes
_DEFAULT_STALE_THRESHOLD_SECONDS = 1800


def _extract_producer_result(dl_status: dict[str, Any]) -> dict[str, Any]:
    """Extract relevant fields from downloader job status for Hub result_json."""
    return {
        "collect_total": dl_status.get("collect_total"),
        "collect_done": dl_status.get("collect_done"),
        "collect_failed": dl_status.get("collect_failed"),
        "row_count": dl_status.get("row_count"),
        "message_count": dl_status.get("message_count"),
        "outbox_delivered": dl_status.get("outbox_delivered"),
        "outbox_failed": dl_status.get("outbox_failed"),
        "current_message": dl_status.get("current_message"),
    }


def poll_downloader_jobs(
    store: Any,
    trigger_clients: dict[str, ExternalSyncClient],
    *,
    max_polls: int = 500,
    stale_threshold_seconds: int = _DEFAULT_STALE_THRESHOLD_SECONDS,
) -> dict[str, int]:
    """Poll downloader for non-terminal downloader_sync jobs and sync status.

    Returns summary: {"polled": N, "updated": N, "failed": N, "stale": N}
    """
    summary = {"polled": 0, "updated": 0, "failed": 0, "stale": 0}

    # Find non-terminal jobs that have a downloader_job_id.
    # Exclude fan-out parent jobs (those with children) — they are not
    # real downloader jobs and should not be polled against /sync/jobs/{id}.
    with store.connect() as conn:
        rows = conn.execute(
            """
            SELECT ingestion_job_id, downloader_job_id, plugin_id, status, updated_at
            FROM ingestion_jobs
            WHERE status NOT IN ('succeeded', 'partial', 'failed', 'cancelled')
              AND downloader_job_id IS NOT NULL
              AND NOT EXISTS (
                SELECT 1 FROM ingestion_jobs j2 WHERE j2.parent_job_id = ingestion_jobs.ingestion_job_id
              )
            ORDER BY id DESC LIMIT ?
            """,
            (max_polls,),
        ).fetchall()

    for row in rows:
        job_id = row["ingestion_job_id"]
        dl_job_id = row["downloader_job_id"]
        plugin_id = row["plugin_id"]
        current_status = row["status"]

        client = trigger_clients.get(plugin_id) if plugin_id else None
        if client is None:
            continue

        dl_status = client.get_job_status(dl_job_id)
        if dl_status is None:
            continue

        summary["polled"] += 1
        dl_raw_status = dl_status.get("status", "")
        mapped_status = _DOWNLOADER_STATUS_MAP.get(dl_raw_status)

        if mapped_status and mapped_status != current_status:
            error = None
            if mapped_status in ("failed", "partial"):
                error = dl_status.get("current_message") or dl_status.get("error") or None
            producer_result = _extract_producer_result(dl_status)
            store.mark_job(job_id, status=mapped_status, producer_status=dl_status, result=producer_result, error=error)
            summary["updated"] += 1
            if mapped_status == "failed":
                summary["failed"] += 1
                logger.warning("downloader job %s -> failed: %s", dl_job_id, error)
        elif mapped_status and mapped_status == current_status:
            # Status unchanged — update producer_status_json anyway
            producer_result = _extract_producer_result(dl_status)
            store.mark_job(job_id, status=current_status, producer_status=dl_status, result=producer_result)

    # Mark stale jobs (non-terminal for too long based on started_at).
    # Exclude fan-out parent jobs (those with children) — their terminal
    # state is determined solely by _aggregate_parent_jobs.
    # Use Python-side threshold calculation since timestamps are Beijing time.
    from datetime import timedelta as _td
    from .time_utils import datahub_now
    stale_cutoff = (datahub_now() - _td(seconds=stale_threshold_seconds)).strftime("%Y-%m-%d %H:%M:%S")
    with store.connect() as conn:
        stale_rows = conn.execute(
            """
            SELECT ingestion_job_id FROM ingestion_jobs
            WHERE status NOT IN ('succeeded', 'partial', 'failed', 'cancelled')
              AND downloader_job_id IS NOT NULL
              AND parent_job_id IS NULL
              AND NOT EXISTS (
                SELECT 1 FROM ingestion_jobs j2 WHERE j2.parent_job_id = ingestion_jobs.ingestion_job_id
              )
              AND started_at < ?
            """,
            (stale_cutoff,),
        ).fetchall()
    for row in stale_rows:
        store.mark_job(row["ingestion_job_id"], status="failed", error="job stale: no status update within threshold")
        summary["stale"] += 1

    # Aggregate parent job status from children
    _aggregate_parent_jobs(store)

    return summary


def _aggregate_parent_jobs(store: Any) -> None:
    """Update parent job status based on child job statuses.

    Skips parents that have a fanout_runs row — the fan-out scheduler
    owns those parents' final status.
    Also skips parents with fan_out_in_progress=True (legacy).
    """
    with store.connect() as conn:
        # Find parent jobs that are still non-terminal
        parents = conn.execute(
            """
            SELECT DISTINCT j1.ingestion_job_id, j1.result_json
            FROM ingestion_jobs j1
            WHERE j1.parent_job_id IS NULL
              AND j1.status NOT IN ('succeeded', 'partial', 'failed', 'cancelled')
              AND EXISTS (
                SELECT 1 FROM ingestion_jobs j2 WHERE j2.parent_job_id = j1.ingestion_job_id
              )
            """,
        ).fetchall()

    for parent_row in parents:
        parent_id = parent_row["ingestion_job_id"]

        # Skip parents managed by the fan-out scheduler
        if store.has_fanout_run(parent_id):
            continue

        # Skip parents that are still in the process of creating children (legacy)
        result_json_str = parent_row["result_json"]
        if result_json_str:
            try:
                rj = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                if rj.get("fan_out_in_progress"):
                    continue
            except (json.JSONDecodeError, TypeError):
                pass
        with store.connect() as conn:
            children = conn.execute(
                "SELECT status, error FROM ingestion_jobs WHERE parent_job_id = ?",
                (parent_id,),
            ).fetchall()

        if not children:
            continue

        total = len(children)
        terminal = [c for c in children if c["status"] in _TERMINAL_STATUSES]
        if len(terminal) < total:
            # Not all children are terminal yet — parent stays running
            continue

        succeeded = sum(1 for c in terminal if c["status"] == "succeeded")
        failed = sum(1 for c in terminal if c["status"] == "failed")
        partial = sum(1 for c in terminal if c["status"] == "partial")

        if failed == 0 and partial == 0:
            parent_status = "succeeded"
        elif succeeded == 0:
            parent_status = "failed"
        else:
            parent_status = "partial"

        errors = [c["error"] for c in terminal if c["error"]]
        error_msg = "; ".join(errors[:3]) if errors else None
        result = {"total": total, "succeeded": succeeded, "failed": failed, "partial": partial}
        store.mark_job(parent_id, status=parent_status, result=result, error=error_msg)
