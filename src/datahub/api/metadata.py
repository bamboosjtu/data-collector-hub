from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.datahub.core.registry import SchemaRegistry
from src.datahub.core.specs import PluginSpec


def build_metadata_router(plugins: list[PluginSpec], registry: SchemaRegistry) -> APIRouter:
    router = APIRouter()

    @router.get("/metadata")
    def metadata() -> dict[str, Any]:
        return {
            "service": "datahub",
            "modes": ["sync trigger", "http callback ingestion", "query"],
            "plugins": [_plugin_dict(plugin, registry) for plugin in plugins],
            "tables": list(registry.tables),
        }

    @router.get("/plugins")
    def list_plugins() -> dict[str, Any]:
        return {"items": [_plugin_dict(plugin, registry) for plugin in plugins]}

    @router.get("/schemas")
    def schemas() -> dict[str, Any]:
        return registry.as_dict()

    @router.get("/schemas/{table_name}")
    def schema(table_name: str) -> dict[str, Any]:
        try:
            registry.require_table(table_name)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return registry.as_dict()["tables"][table_name]

    return router


def _plugin_dict(plugin: PluginSpec, registry: SchemaRegistry) -> dict[str, Any]:
    datasets = {
        table.dataset_key
        for table in registry.tables.values()
        if plugin.tables_path is not None and table.table_name in (registry.raw.get("tables") or {})
    }
    return {
        "name": plugin.name,
        "version": plugin.version,
        "label": plugin.display.label,
        "description": plugin.display.description,
        "connector_type": plugin.connector.type,
        "commands": [
            {
                "name": command.name,
                "description": command.description,
                "required_params": list(command.required_params),
                "enabled": command.enabled,
                "trigger_type": command.trigger.get("type", ""),
            }
            for command in plugin.commands
        ],
        "query_routes": [route.path for route in plugin.query_routes],
        "datasets": sorted(datasets),
    }
