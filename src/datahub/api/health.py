from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from src.datahub.core.registry import SchemaRegistry


def build_health_router(registry: SchemaRegistry) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "service": "datahub", "schema_version": registry.version}

    @router.get("/")
    def root() -> dict[str, Any]:
        return {"service": "DataHub MVP", "docs": "/docs", "health": "/health"}

    return router
