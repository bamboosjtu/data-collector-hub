from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .specs import CommandSpec, ConnectorSpec, DisplaySpec, PluginSpec, QueryRouteSpec, ScopeMapping


def load_plugin(plugin_dir: Path) -> PluginSpec:
    config_path = plugin_dir / "plugin.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    display_payload = payload.get("display") or {}
    connector_payload = payload.get("connector") or {}

    plugin = PluginSpec(
        name=str(payload.get("name", plugin_dir.name)),
        version=int(payload.get("version", 1)),
        display=DisplaySpec(
            label=str(display_payload.get("label", plugin_dir.name)),
            description=str(display_payload.get("description", "")),
        ),
        connector=ConnectorSpec(
            type=str(connector_payload.get("type", "external_sync")),
            base_url=str(connector_payload.get("base_url", "http://localhost:8010")),
            timeout_seconds=int(connector_payload.get("timeout_seconds", 30)),
        ),
        commands=tuple(_parse_command(item) for item in (payload.get("commands") or [])),
        query_routes=tuple(_parse_query_route(item) for item in (payload.get("query_routes") or [])),
        scope_mappings=tuple(_parse_scope_mapping(item) for item in (payload.get("scope_mappings") or [])),
        tables_path=(plugin_dir / "tables.yaml") if (plugin_dir / "tables.yaml").exists() else None,
    )
    _validate_plugin(plugin)
    return plugin


def load_all_plugins(plugins_dir: Path) -> list[PluginSpec]:
    if not plugins_dir.is_dir():
        return []
    return [load_plugin(item) for item in sorted(plugins_dir.iterdir()) if item.is_dir() and (item / "plugin.yaml").exists()]


def build_scope_map(plugins: list[PluginSpec]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for plugin in plugins:
        for mapping in plugin.scope_mappings:
            result[mapping.table] = dict(mapping.map)
    return result


def find_command(plugins: list[PluginSpec], job_type: str) -> CommandSpec | None:
    for plugin in plugins:
        for command in plugin.commands:
            if command.job_type == job_type:
                return command
    return None


def find_plugin_for_job(plugins: list[PluginSpec], job_type: str) -> PluginSpec | None:
    for plugin in plugins:
        if any(command.job_type == job_type for command in plugin.commands):
            return plugin
    return None


def _parse_command(item: dict[str, Any]) -> CommandSpec:
    return CommandSpec(job_type=str(item["job_type"]), required_params=tuple(item.get("required_params") or ()))


def _parse_query_route(item: dict[str, Any]) -> QueryRouteSpec:
    return QueryRouteSpec(
        path=str(item["path"]),
        table=str(item["table"]),
        path_filters=dict(item.get("path_filters") or {}),
        query_filters=dict(item.get("query_filters") or {}),
        default_limit=int(item.get("default_limit", 200)),
        max_limit=int(item.get("max_limit", 200)),
    )


def _parse_scope_mapping(item: dict[str, Any]) -> ScopeMapping:
    return ScopeMapping(table=str(item["table"]), map=dict(item.get("map") or {}))


def _validate_plugin(plugin: PluginSpec) -> None:
    seen_jobs: set[str] = set()
    for command in plugin.commands:
        if command.job_type in seen_jobs:
            raise ValueError(f"duplicate job_type in plugin {plugin.name}: {command.job_type}")
        seen_jobs.add(command.job_type)
    seen_routes: set[str] = set()
    for route in plugin.query_routes:
        if not route.path.startswith("/"):
            raise ValueError(f"query route path must start with /: {route.path}")
        if route.path in seen_routes:
            raise ValueError(f"duplicate query route in plugin {plugin.name}: {route.path}")
        seen_routes.add(route.path)
