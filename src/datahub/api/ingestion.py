from __future__ import annotations

import json
import logging
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from src.datahub.core.plugin_loader import find_command, find_plugin_for_job
from src.datahub.core.fan_out import load_plugin_handler, build_handler_context, run_handler_async
from src.datahub.core.specs import PluginSpec
from src.datahub.core.trigger_runtime import ExternalSyncClient, new_producer_job_id
from src.datahub.ingestion.models import TableBatchPayload
from src.datahub.ingestion.service import IngestionService
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope

logger = logging.getLogger(__name__)


class IngestionJobRequest(BaseModel):
    command: str
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
        result = ingestion_service.ingest_table_batch(payload.model_dump())
        if result["status"] in {"failed", "conflict"}:
            logger.error("ingest_table_batch returned %s: %s", result["status"], result)
            code = status.HTTP_409_CONFLICT if result["status"] == "conflict" else status.HTTP_422_UNPROCESSABLE_ENTITY
            if result.get("error_code") == "storage_error":
                code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=code, detail=result)
        return result

    @router.post("/ingestion/v1/jobs", status_code=202, dependencies=[Depends(require_scope(store, "ingestion"))])
    def create_ingestion_job(payload: IngestionJobRequest) -> dict[str, Any]:
        command = find_command(plugins, payload.command)
        plugin = find_plugin_for_job(plugins, payload.command)
        if command is None or plugin is None:
            raise HTTPException(status_code=422, detail={"error": "unknown_command", "message": f"command {payload.command} not declared by any plugin"})
        if not command.enabled:
            raise HTTPException(status_code=422, detail={"error": "command_disabled", "message": f"command {payload.command} is currently disabled"})
        for param in command.required_params:
            if param not in payload.params or payload.params[param] is None:
                raise HTTPException(status_code=422, detail={"error": "missing_required_param", "message": f"command {payload.command} requires param {param}"})

        ingestion_job_id = f"ing_{payload.command}_{uuid4().hex[:12]}"
        producer_job_id = payload.downloader_job_id or new_producer_job_id(payload.command, payload.params, command)
        trigger_type = command.trigger.get("type", "downloader_sync")

        # Plugin handler trigger: delegate execution to a plugin-declared handler
        if trigger_type == "plugin_handler":
            handler_path = command.trigger.get("handler")
            if not handler_path:
                raise HTTPException(status_code=422, detail={"error": "invalid_trigger", "message": f"command {payload.command} trigger has no handler"})

            store.create_ingestion_job(
                ingestion_job_id=ingestion_job_id,
                producer_job_id=producer_job_id,
                job_type=payload.command,
                params=payload.params,
                plugin_id=plugin.name,
            )
            store.mark_job(ingestion_job_id, status="running")
            try:
                handler = load_plugin_handler(handler_path, plugin_name=plugin.name)
                callback_headers = {"X-API-Key": settings.callback_api_key} if settings.callback_api_key else None
                ctx = build_handler_context(
                    store=store,
                    plugins=plugins,
                    trigger_clients=trigger_clients,
                    ingestion_job_id=ingestion_job_id,
                    callback_base_url=settings.callback_base_url,
                    callback_headers=callback_headers,
                    params=payload.params,
                    command=command,
                    plugin=plugin,
                )
                # Run handler in background thread
                run_handler_async(handler, ctx)
            except Exception as exc:
                store.mark_job(ingestion_job_id, status="failed", error=str(exc))
                raise HTTPException(status_code=500, detail={"error": "plugin_handler_failed", "message": str(exc)}) from exc
            return {"ingestion_job_id": ingestion_job_id, "status": "running", "message": "plugin_handler started in background"}

        # Default: downloader_sync trigger
        store.create_ingestion_job(
            ingestion_job_id=ingestion_job_id,
            producer_job_id=producer_job_id,
            job_type=payload.command,
            params=payload.params,
            plugin_id=plugin.name,
        )
        client = trigger_clients.get(plugin.name)
        if client is None:
            store.mark_job(ingestion_job_id, status="failed", error="no external trigger connector configured")
            raise HTTPException(status_code=502, detail={"error": "no_connector", "message": f"no connector configured for command {payload.command}"})

        # Resolve downloader job_type from command.trigger
        downloader_job_type = command.trigger.get("job_type")
        if not downloader_job_type:
            store.mark_job(ingestion_job_id, status="failed", error="command trigger has no job_type")
            raise HTTPException(status_code=422, detail={"error": "invalid_trigger", "message": f"command {payload.command} trigger has no job_type"})

        callback_url = f"{settings.callback_base_url}/ingestion/v1/table-batches"
        callback_headers = {"X-API-Key": settings.callback_api_key} if settings.callback_api_key else None
        try:
            response = client.sync(
                producer_job_id=producer_job_id,
                job_type=downloader_job_type,
                params=payload.params,
                callback_url=callback_url,
                callback_headers=callback_headers,
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

    @router.get("/ingestion/v1/jobs/{ingestion_job_id}/children", dependencies=[Depends(require_scope(store, "admin"))])
    def list_child_jobs(ingestion_job_id: str) -> dict[str, Any]:
        children = store.list_child_jobs(ingestion_job_id)
        return {"parent_job_id": ingestion_job_id, "total": len(children), "items": children}

    @router.post("/ingestion/v1/jobs/{ingestion_job_id}/retry", status_code=202, dependencies=[Depends(require_scope(store, "ingestion"))])
    def retry_ingestion_job(ingestion_job_id: str) -> dict[str, Any]:
        """Retry a failed job by re-creating it with the same command and params."""
        original = store.get_job(ingestion_job_id)
        if not original:
            raise HTTPException(status_code=404, detail="ingestion job not found")
        command_name = original.get("trigger_key")
        if not command_name:
            raise HTTPException(status_code=422, detail="original job has no command")
        params = json.loads(original.get("params_json") or "{}")
        payload = IngestionJobRequest(command=command_name, params=params)
        return create_ingestion_job(payload)

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
