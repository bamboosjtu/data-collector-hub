from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TablePayload(BaseModel):
    table_name: str
    scope_values: dict[str, Any] = Field(default_factory=dict)
    rows: list[dict[str, Any]] = Field(default_factory=list)


class TableBatchPayload(BaseModel):
    message_id: str
    idempotency_key: str
    downloader_job_id: str
    collect_run_id: str
    dataset_key: str
    scope_key: str | None = None
    payload_hash: str
    tables: list[TablePayload]
