from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.datahub.core.plugin_loader import find_command, find_plugin_for_job
from src.datahub.core.specs import PluginSpec
from src.datahub.core.trigger_runtime import ExternalSyncClient, new_producer_job_id
from src.datahub.ingestion.models import TableBatchPayload
from src.datahub.ingestion.service import IngestionService
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope


class IngestionJobRequest(BaseModel):
    job_type: str
    params: dict[str, Any] = Field(default_factory=dict)
    downloader_job_id: str | None = None
    debug: bool = False


def build_ingestion_router(
    *,
    settings: Settings,
    plugins: list[PluginSpec],
    store: DataHubStore,
    trigger_clients: dict[str, ExternalSyncClient],
    ingestion_service: IngestionService,
) -> APIRouter:
    router = APIRouter()

    @router.post("/ingestion/v1/table-batches", dependencies=[Depends(require_scope(store, "ingestion"))])
    def ingest_table_batch(payload: TableBatchPayload) -> dict[str, Any]:
        result = ingestion_service.ingest_table_batch(payload.model_dump())
        if result["status"] in {"failed", "conflict"}:
            code = status.HTTP_409_CONFLICT if result["status"] == "conflict" else status.HTTP_422_UNPROCESSABLE_ENTITY
            if result.get("error_code") == "storage_error":
                code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=code, detail=result)
        return result

    @router.post("/ingestion/v1/jobs", status_code=202, dependencies=[Depends(require_scope(store, "ingestion"))])
    def create_ingestion_job(payload: IngestionJobRequest) -> dict[str, Any]:
        command = find_command(plugins, payload.job_type)
        plugin = find_plugin_for_job(plugins, payload.job_type)
        if command is None or plugin is None:
            raise HTTPException(status_code=422, detail={"error": "unknown_job_type", "message": f"job_type {payload.job_type} not declared by any plugin"})
        for param in command.required_params:
            if param not in payload.params or payload.params[param] is None:
                raise HTTPException(status_code=422, detail={"error": "missing_required_param", "message": f"job_type {payload.job_type} requires param {param}"})

        ingestion_job_id = f"ing_{payload.job_type}_{uuid4().hex[:12]}"
        producer_job_id = payload.downloader_job_id or new_producer_job_id(payload.job_type, payload.params, command)
        store.create_ingestion_job(
            ingestion_job_id=ingestion_job_id,
            producer_job_id=producer_job_id,
            job_type=payload.job_type,
            params=payload.params,
            plugin_id=plugin.name,
        )
        client = trigger_clients.get(plugin.name)
        if client is None:
            store.mark_job(ingestion_job_id, status="failed", error="no external trigger connector configured")
            raise HTTPException(status_code=502, detail={"error": "no_connector", "message": f"no connector configured for job_type {payload.job_type}"})
        callback_url = f"{settings.callback_base_url}/ingestion/v1/table-batches"
        try:
            response = client.sync(
                producer_job_id=producer_job_id,
                job_type=payload.job_type,
                params=payload.params,
                callback_url=callback_url,
                debug=payload.debug,
            )
        except Exception as exc:
            store.mark_job(ingestion_job_id, status="failed", error=str(exc))
            raise HTTPException(status_code=502, detail={"error": "external_sync_failed", "message": str(exc)}) from exc
        store.mark_job(ingestion_job_id, status=str(response.get("status") or "accepted"), producer_status=response)
        return {"ingestion_job_id": ingestion_job_id, "downloader_job_id": producer_job_id, "status": response.get("status", "accepted")}

    @router.get("/ingestion/v1/jobs", dependencies=[Depends(require_scope(store, "admin"))])
    def list_jobs(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        return {"items": store.list_jobs(limit)}

    @router.get("/ingestion/v1/jobs/{ingestion_job_id}", dependencies=[Depends(require_scope(store, "admin"))])
    def get_job(ingestion_job_id: str) -> dict[str, Any]:
        row = store.get_job(ingestion_job_id)
        if not row:
            raise HTTPException(status_code=404, detail="ingestion job not found")
        return row

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
