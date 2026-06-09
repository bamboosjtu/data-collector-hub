from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any

import yaml

from .specs import CommandSpec, ConnectorSpec, DisplaySpec, NormalizerSpec, PluginSpec, QueryRouteSpec, ScopeMapping

logger = logging.getLogger(__name__)


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
        normalizers=tuple(_parse_normalizer(item) for item in (payload.get("normalizers") or [])),
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


def build_normalizer_map(plugins: list[PluginSpec]) -> dict[str, tuple[NormalizerSpec, PluginSpec]]:
    """Build source_table -> (NormalizerSpec, PluginSpec) mapping."""
    result: dict[str, tuple[NormalizerSpec, PluginSpec]] = {}
    for plugin in plugins:
        for norm in plugin.normalizers:
            result[norm.source_table] = (norm, plugin)
    return result


def find_command(plugins: list[PluginSpec], name: str) -> CommandSpec | None:
    for plugin in plugins:
        for command in plugin.commands:
            if command.name == name and command.enabled:
                return command
    return None


def find_plugin_for_job(plugins: list[PluginSpec], name: str) -> PluginSpec | None:
    for plugin in plugins:
        if any(command.name == name and command.enabled for command in plugin.commands):
            return plugin
    return None


def load_normalizer_handler(plugin: PluginSpec, normalizer: NormalizerSpec) -> Any:
    """Load normalizer handler function, restricted to the plugin's own module path.

    Handler format in YAML: ``dcp.normalizers:normalize_plan_sgcc_year``
    The prefix before the dot must match the plugin name.
    """
    handler_ref = normalizer.handler
    if ":" not in handler_ref:
        raise ValueError(f"normalizer handler must be in 'module:function' format, got: {handler_ref}")
    module_part, func_name = handler_ref.split(":", 1)
    prefix = module_part.split(".")[0]
    if prefix != plugin.name:
        raise ValueError(
            f"normalizer handler '{handler_ref}' must be scoped to plugin '{plugin.name}' "
            f"(expected prefix '{plugin.name}.xxx', got '{prefix}')"
        )
    full_module = f"plugins.{module_part}"
    try:
        mod = importlib.import_module(full_module)
    except ImportError as exc:
        raise ImportError(f"cannot import normalizer module '{full_module}': {exc}") from exc
    handler = getattr(mod, func_name, None)
    if handler is None:
        raise AttributeError(f"module '{full_module}' has no function '{func_name}'")
    return handler


def _parse_command(item: dict[str, Any]) -> CommandSpec:
    mc = max(1, int(item.get("max_concurrency", 1)))
    raw_limit = item.get("max_concurrency_limit")
    limit = max(mc, int(raw_limit)) if raw_limit is not None else None
    cooldown = max(0.0, float(item.get("cooldown_seconds", 0.0)))
    return CommandSpec(
        name=str(item.get("name") or item.get("job_type", "")),
        description=str(item.get("description", "")),
        required_params=tuple(item.get("required_params") or ()),
        trigger=dict(item.get("trigger") or {}),
        enabled=bool(item.get("enabled", True)),
        max_concurrency=mc,
        max_concurrency_limit=limit,
        cooldown_seconds=cooldown,
    )


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


def _parse_normalizer(item: dict[str, Any]) -> NormalizerSpec:
    return NormalizerSpec(
        source_table=str(item["source_table"]),
        targets=tuple(item.get("targets") or []),
        handler=str(item["handler"]),
    )


def _validate_plugin(plugin: PluginSpec) -> None:
    seen_names: set[str] = set()
    for command in plugin.commands:
        if command.name in seen_names:
            raise ValueError(f"duplicate command name in plugin {plugin.name}: {command.name}")
        seen_names.add(command.name)
    seen_routes: set[str] = set()
    for route in plugin.query_routes:
        if not route.path.startswith("/"):
            raise ValueError(f"query route path must start with /: {route.path}")
        if route.path in seen_routes:
            raise ValueError(f"duplicate query route in plugin {plugin.name}: {route.path}")
        seen_routes.add(route.path)
