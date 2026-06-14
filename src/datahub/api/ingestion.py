from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from src.datahub.core.services.job_service import JobService, JobServiceError
from src.datahub.core.specs import PluginSpec
from src.datahub.core.trigger_runtime import ExternalSyncClient
from src.datahub.ingestion.models import TableBatchPayload
from src.datahub.ingestion.service import IngestionService
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope

logger = logging.getLogger(__name__)


_ERROR_STATUS_MAP: dict[str, int] = {
    "unknown_command": 422,
    "command_disabled": 422,
    "missing_required_param": 422,
    "invalid_trigger": 422,
    "invalid_source": 422,
    "no_connector": 502,
    "external_sync_failed": 502,
    "plugin_handler_failed": 500,
    "job_not_found": 404,
    "no_command": 422,
    "job_not_retryable": 409,
}


def _error_status(error_code: str) -> int:
    return _ERROR_STATUS_MAP.get(error_code, 500)


class IngestionJobRequest(BaseModel):
    command: str
    params: dict[str, Any] = Field(default_factory=dict)
    downloader_job_id: str | None = None
    source: str = "api"
    debug: bool = False


def build_ingestion_router(
    *,
    settings: Settings,
    plugins: list[PluginSpec],
    store: DataHubStore,
    trigger_clients: dict[str, ExternalSyncClient],
    ingestion_service: IngestionService,
    job_service: JobService | None = None,
) -> APIRouter:
    router = APIRouter()
    _job_service = job_service or JobService(
        store=store,
        plugins=plugins,
        trigger_clients=trigger_clients,
        callback_base_url=settings.callback_base_url,
        callback_headers={"X-API-Key": settings.callback_api_key} if settings.callback_api_key else None,
    )

    @router.post("/ingestion/v1/table-batches", dependencies=[Depends(require_scope(store, "ingestion"))])
    async def ingest_table_batch(request: Request) -> dict[str, Any]:
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8", errors="replace")
        try:
            raw = json.loads(body_text)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in table-batches: %s", e)
            raise HTTPException(status_code=422, detail={"error": "invalid_json", "message": str(e)}) from e
        try:
            payload = TableBatchPayload.model_validate(raw)
        except Exception as e:
            logger.error("Pydantic validation failed: %s\nBody preview: %s", e, body_text[:2000])
            raise HTTPException(status_code=422, detail={"error": "validation_failed", "message": str(e), "body_preview": body_text[:500]}) from e
        result = await asyncio.to_thread(ingestion_service.ingest_table_batch, payload.model_dump())
        if result["status"] in {"failed", "conflict"}:
            logger.error("ingest_table_batch returned %s: %s", result["status"], result)
            code = status.HTTP_409_CONFLICT if result["status"] == "conflict" else status.HTTP_422_UNPROCESSABLE_ENTITY
            if result.get("error_code") == "storage_error":
                code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=code, detail=result)
        return result

    @router.post("/ingestion/v1/jobs", status_code=202, dependencies=[Depends(require_scope(store, "ingestion"))])
    def create_ingestion_job(payload: IngestionJobRequest) -> dict[str, Any]:
        try:
            result = _job_service.submit_command(payload.command, payload.params, source=payload.source)
        except JobServiceError as exc:
            status_code = _error_status(exc.error_code)
            detail: dict[str, Any] = {"error": exc.error_code, "message": exc.message}
            if exc.ingestion_job_id:
                detail["ingestion_job_id"] = exc.ingestion_job_id
            raise HTTPException(status_code=status_code, detail=detail) from exc
        resp: dict[str, Any] = {"ingestion_job_id": result.ingestion_job_id, "status": result.status}
        if result.downloader_job_id:
            resp["downloader_job_id"] = result.downloader_job_id
        if result.message:
            resp["message"] = result.message
        return resp

    @router.get("/ingestion/v1/jobs", dependencies=[Depends(require_scope(store, "admin"))])
    def list_jobs(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        return {"items": store.list_jobs(limit)}

    @router.get("/ingestion/v1/jobs/{ingestion_job_id}", dependencies=[Depends(require_scope(store, "admin"))])
    def get_job(ingestion_job_id: str) -> dict[str, Any]:
        row = store.get_job(ingestion_job_id)
        if not row:
            raise HTTPException(status_code=404, detail="ingestion job not found")
        return row

    @router.get("/ingestion/v1/jobs/{ingestion_job_id}/children", dependencies=[Depends(require_scope(store, "admin"))])
    def list_child_jobs(ingestion_job_id: str) -> dict[str, Any]:
        children = store.list_child_jobs(ingestion_job_id)
        return {"parent_job_id": ingestion_job_id, "total": len(children), "items": children}

    @router.post("/ingestion/v1/jobs/{ingestion_job_id}/retry", status_code=202, dependencies=[Depends(require_scope(store, "ingestion"))])
    def retry_ingestion_job(ingestion_job_id: str) -> dict[str, Any]:
        """Retry a failed job by re-creating it with the same command and params."""
        try:
            result = _job_service.retry_job(ingestion_job_id)
        except JobServiceError as exc:
            status_code = _error_status(exc.error_code)
            raise HTTPException(status_code=status_code, detail={"error": exc.error_code, "message": exc.message}) from exc
        resp: dict[str, Any] = {"ingestion_job_id": result.ingestion_job_id, "status": result.status}
        if result.downloader_job_id:
            resp["downloader_job_id"] = result.downloader_job_id
        if result.original_job_id:
            resp["original_job_id"] = result.original_job_id
        return resp

    @router.get("/ingestion/v1/messages", dependencies=[Depends(require_scope(store, "admin"))])
    def list_messages(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        return {"items": store.list_messages(limit)}

    @router.get("/ingestion/v1/messages/{message_id}", dependencies=[Depends(require_scope(store, "admin"))])
    def get_message(message_id: str) -> dict[str, Any]:
        row = store.get_message(message_id)
        if not row:
            raise HTTPException(status_code=404, detail="ingestion message not found")
        return row

    @router.get("/ingestion/v1/table-writes", dependencies=[Depends(require_scope(store, "admin"))])
    def table_writes(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        return {"items": store.list_table_writes(limit)}

    return router
