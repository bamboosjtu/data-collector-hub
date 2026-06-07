from __future__ import annotations

import json
from typing import Any
from urllib import request
from uuid import uuid4

from .specs import CommandSpec, ConnectorSpec


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

# Stale threshold: if a job hasn't been updated for this many seconds, mark stale
_STALE_THRESHOLD_SECONDS = 600  # 10 minutes


def poll_downloader_jobs(
    store: Any,
    trigger_clients: dict[str, ExternalSyncClient],
    *,
    max_polls: int = 50,
) -> dict[str, int]:
    """Poll downloader for non-terminal downloader_sync jobs and sync status.

    Returns summary: {"polled": N, "updated": N, "failed": N, "stale": N}
    """
    summary = {"polled": 0, "updated": 0, "failed": 0, "stale": 0}

    # Find non-terminal jobs that have a downloader_job_id
    with store.connect() as conn:
        rows = conn.execute(
            """
            SELECT ingestion_job_id, downloader_job_id, plugin_id, status, updated_at
            FROM ingestion_jobs
            WHERE status NOT IN ('succeeded', 'partial', 'failed', 'cancelled')
              AND downloader_job_id IS NOT NULL
              AND parent_job_id IS NULL
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
            store.mark_job(job_id, status=mapped_status, producer_status=dl_status, error=error)
            summary["updated"] += 1
            if mapped_status == "failed":
                summary["failed"] += 1
                logger.warning("downloader job %s -> failed: %s", dl_job_id, error)
        elif mapped_status and mapped_status == current_status:
            # Status unchanged — update producer_status_json anyway
            store.mark_job(job_id, status=current_status, producer_status=dl_status)

    # Mark stale jobs (non-terminal for too long)
    with store.connect() as conn:
        stale_rows = conn.execute(
            """
            SELECT ingestion_job_id FROM ingestion_jobs
            WHERE status NOT IN ('succeeded', 'partial', 'failed', 'cancelled')
              AND downloader_job_id IS NOT NULL
              AND parent_job_id IS NULL
              AND updated_at < datetime('now', ?)
            """,
            (f"-{_STALE_THRESHOLD_SECONDS} seconds",),
        ).fetchall()
    for row in stale_rows:
        store.mark_job(row["ingestion_job_id"], status="failed", error="job stale: no status update within threshold")
        summary["stale"] += 1

    return summary


import logging

logger = logging.getLogger(__name__)
