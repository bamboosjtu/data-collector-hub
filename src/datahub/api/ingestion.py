from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.datahub.core.plugin_loader import find_command, find_plugin_for_job
from src.datahub.core.fan_out import (
    DateRangeFanOutConfig,
    FanOutConfig,
    execute_date_range_fan_out_async,
    execute_fan_out_async,
    resolve_auto_params,
)
from src.datahub.core.specs import PluginSpec
from src.datahub.core.trigger_runtime import ExternalSyncClient, new_producer_job_id
from src.datahub.ingestion.models import TableBatchPayload
from src.datahub.ingestion.service import IngestionService
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope


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

        # Resolve auto_params (yesterday, today, etc.) before any trigger logic
        auto_params = command.trigger.get("auto_params")
        if auto_params:
            payload.params = {**resolve_auto_params(auto_params, payload.params), **payload.params}

        # Fan-out trigger: query source table, trigger child command for each row
        if trigger_type == "fan_out":
            store.create_ingestion_job(
                ingestion_job_id=ingestion_job_id,
                producer_job_id=producer_job_id,
                job_type=payload.command,
                params=payload.params,
                plugin_id=plugin.name,
            )
            store.mark_job(ingestion_job_id, status="running")
            try:
                fan_out_config = FanOutConfig.from_trigger(command.trigger)
                max_items = payload.params.get("max_items")
                if max_items is not None:
                    max_items = int(max_items)
                execute_fan_out_async(
                    fan_out_config=fan_out_config,
                    store=store,
                    plugins=plugins,
                    trigger_clients=trigger_clients,
                    parent_job_id=ingestion_job_id,
                    callback_base_url=settings.callback_base_url,
                    max_items=max_items,
                )
            except Exception as exc:
                store.mark_job(ingestion_job_id, status="failed", error=str(exc))
                raise HTTPException(status_code=500, detail={"error": "fan_out_failed", "message": str(exc)}) from exc
            return {"ingestion_job_id": ingestion_job_id, "status": "running", "message": "fan-out started in background"}

        # Date-range fan-out: split date range into chunks, trigger child command per chunk
        if trigger_type == "date_range_fan_out":
            store.create_ingestion_job(
                ingestion_job_id=ingestion_job_id,
                producer_job_id=producer_job_id,
                job_type=payload.command,
                params=payload.params,
                plugin_id=plugin.name,
            )
            store.mark_job(ingestion_job_id, status="running")
            try:
                dr_config = DateRangeFanOutConfig.from_trigger(command.trigger)
                # Allow chunk_days override from params
                if "chunk_days" in payload.params:
                    dr_config = DateRangeFanOutConfig(
                        child_command=dr_config.child_command,
                        start_date_param=dr_config.start_date_param,
                        end_date_param=dr_config.end_date_param,
                        chunk_days=int(payload.params["chunk_days"]),
                        fallback_chunk_days=dr_config.fallback_chunk_days,
                        cooldown_seconds=dr_config.cooldown_seconds,
                        date_format=dr_config.date_format,
                    )
                execute_date_range_fan_out_async(
                    config=dr_config,
                    params=payload.params,
                    store=store,
                    plugins=plugins,
                    trigger_clients=trigger_clients,
                    parent_job_id=ingestion_job_id,
                    callback_base_url=settings.callback_base_url,
                )
            except Exception as exc:
                store.mark_job(ingestion_job_id, status="failed", error=str(exc))
                raise HTTPException(status_code=500, detail={"error": "date_range_fan_out_failed", "message": str(exc)}) from exc
            return {"ingestion_job_id": ingestion_job_id, "status": "running", "message": "date-range fan-out started in background"}

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
        try:
            response = client.sync(
                producer_job_id=producer_job_id,
                job_type=downloader_job_type,
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
