from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .specs import ColumnSpec, PluginSpec, TableSpec


class SchemaRegistry:
    def __init__(self, *, version: int, tables: dict[str, TableSpec], datasets: set[str], raw: dict[str, Any]):
        self.version = version
        self.tables = tables
        self.datasets = datasets
        self.raw = raw

    def require_table(self, table_name: str) -> TableSpec:
        try:
            return self.tables[table_name]
        except KeyError as exc:
            raise ValueError(f"unknown_table: {table_name}") from exc

    def require_dataset(self, dataset_key: str) -> None:
        if dataset_key not in self.datasets:
            raise ValueError(f"unknown_dataset: {dataset_key}")

    def as_dict(self) -> dict[str, Any]:
        return self.raw


def load_registry(path: str | Path) -> SchemaRegistry:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return _registry_from_table_payloads([(None, payload)])


def load_registry_from_plugins(plugins: list[PluginSpec]) -> SchemaRegistry:
    payloads: list[tuple[PluginSpec | None, dict[str, Any]]] = []
    for plugin in plugins:
        if plugin.tables_path is None:
            continue
        payloads.append((plugin, yaml.safe_load(plugin.tables_path.read_text(encoding="utf-8")) or {}))
    registry = _registry_from_table_payloads(payloads)
    _validate_routes(plugins, registry)
    return registry


def validate_row(table: TableSpec, row: dict[str, Any]) -> dict[str, Any]:
    extra_column = table.columns.get("extra")
    has_extra = extra_column is not None and extra_column.type == "json"
    unknown = sorted(set(row) - set(table.columns))
    if unknown and not has_extra:
        raise ValueError(f"schema_mismatch: unknown columns in {table.table_name}: {', '.join(unknown)}")
    normalized: dict[str, Any] = {}
    overflow: dict[str, Any] = {}
    for key, value in row.items():
        if key in table.columns:
            continue
        overflow[key] = value
    for name, column in table.columns.items():
        if name == "extra":
            continue
        value = row.get(name)
        if value is None and not column.nullable:
            raise ValueError(f"schema_mismatch: {table.table_name}.{name} is required")
        normalized[name] = _coerce(value, column.type, table.table_name, name)
    if has_extra:
        existing_extra = row.get("extra")
        if isinstance(existing_extra, dict):
            overflow.update(existing_extra)
        normalized["extra"] = overflow if overflow else (existing_extra if existing_extra is not None else None)
    for key in table.primary_key:
        if normalized.get(key) is None:
            raise ValueError(f"missing_primary_key: {table.table_name}.{key} primary key is required")
    return normalized


def validate_scope(table: TableSpec, scope_values: dict[str, Any]) -> None:
    if table.write_mode == "replace_scope":
        missing = [name for name in table.scope_column_names if scope_values.get(name) is None]
        if missing:
            raise ValueError(f"missing_scope_values: {table.table_name} requires scope values: {', '.join(missing)}")


def _registry_from_table_payloads(payloads: list[tuple[PluginSpec | None, dict[str, Any]]]) -> SchemaRegistry:
    all_tables: dict[str, TableSpec] = {}
    raw_tables: dict[str, Any] = {}
    datasets: set[str] = set()
    version = 1
    for _plugin, payload in payloads:
        version = max(version, int(payload.get("version") or 1))
        for table_name, item in (payload.get("tables") or {}).items():
            if table_name in all_tables:
                raise ValueError(f"duplicate table: {table_name}")
            table = _parse_table(table_name, item)
            _validate_table(table)
            all_tables[table_name] = table
            raw_tables[table_name] = item
            datasets.add(table.dataset_key)
    return SchemaRegistry(version=version, tables=all_tables, datasets=datasets, raw={"version": version, "tables": raw_tables})


def _parse_table(table_name: str, item: dict[str, Any]) -> TableSpec:
    columns = {
        name: ColumnSpec(name=name, type=str(spec.get("type") or "string"), nullable=bool(spec.get("nullable", True)))
        for name, spec in (item.get("columns") or {}).items()
    }
    return TableSpec(
        table_name=table_name,
        dataset_key=str(item["dataset_key"]),
        description=str(item.get("description") or ""),
        write_mode=str(item["write_mode"]),
        primary_key=tuple(item.get("primary_key") or ()),
        scope_column_names=tuple(item.get("scope_column_names") or ()),
        columns=columns,
    )


def _validate_table(table: TableSpec) -> None:
    if table.write_mode not in {"upsert", "replace_scope", "append"}:
        raise ValueError(f"unknown write_mode for {table.table_name}: {table.write_mode}")
    for name in table.primary_key + table.scope_column_names:
        if name not in table.columns:
            raise ValueError(f"{table.table_name} references unknown column: {name}")
    if table.write_mode == "upsert" and not table.primary_key:
        raise ValueError(f"{table.table_name} upsert requires primary_key")
    if table.write_mode == "replace_scope" and not table.scope_column_names and not table.primary_key:
        raise ValueError(f"{table.table_name} replace_scope requires scope_column_names or primary_key")


def _validate_routes(plugins: list[PluginSpec], registry: SchemaRegistry) -> None:
    seen: set[str] = set()
    for plugin in plugins:
        for route in plugin.query_routes:
            if route.path in seen:
                raise ValueError(f"duplicate query route path: {route.path}")
            seen.add(route.path)
            registry.require_table(route.table)
            table = registry.tables[route.table]
            for column in list(route.path_filters) + list(route.query_filters):
                if column not in table.columns:
                    raise ValueError(f"query route {route.path} references unknown column {route.table}.{column}")


def _coerce(value: Any, column_type: str, table_name: str, column_name: str) -> Any:
    if value is None:
        return None
    if column_type in {"string", "date"}:
        return str(value)
    if column_type == "integer":
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"schema_mismatch: {table_name}.{column_name} must be integer") from exc
    if column_type == "number":
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"schema_mismatch: {table_name}.{column_name} must be number") from exc
    if column_type == "json":
        return value
    return value
