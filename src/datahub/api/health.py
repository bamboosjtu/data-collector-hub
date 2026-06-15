from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request

from src.datahub.core.registry import SchemaRegistry
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)


def build_health_router(registry: SchemaRegistry, *, store: DataHubStore, settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "service": "datahub", "schema_version": registry.version}

    @router.get("/health/ready")
    def health_ready(request: Request) -> dict[str, Any]:
        db_status = "ok"
        try:
            with store.connect() as conn:
                conn.execute("SELECT 1")
        except Exception:
            logger.exception("readiness DB check failed")
            db_status = "error"

        fanout_stop = getattr(request.app.state, "fanout_scheduler_stop", None)
        fanout_status = "running" if fanout_stop is not None and not fanout_stop.is_set() else "unknown"

        status = "degraded" if db_status == "error" else "ok"
        return {
            "status": status,
            "db": db_status,
            "tables": len(registry.tables),
            "scheduler_enabled": settings.collection_scheduler_enabled,
            "daily_dcp_refresh_enabled": settings.daily_dcp_refresh_enabled,
            "fanout_scheduler": fanout_status,
            "db_path": str(store.db_path),
        }

    @router.get("/")
    def root() -> dict[str, Any]:
        return {"service": "DataHub MVP", "docs": "/docs", "health": "/health"}

    return router
