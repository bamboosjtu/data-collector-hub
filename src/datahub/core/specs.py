from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str = ""
    required_params: tuple[str, ...] = ()
    trigger: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass(frozen=True)
class NormalizerSpec:
    source_table: str
    targets: tuple[str, ...]
    handler: str


@dataclass(frozen=True)
class QueryRouteSpec:
    path: str
    table: str
    path_filters: dict[str, str] = field(default_factory=dict)
    query_filters: dict[str, str] = field(default_factory=dict)
    default_limit: int = 200
    max_limit: int = 200


@dataclass(frozen=True)
class ScopeMapping:
    table: str
    map: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectorSpec:
    type: str
    base_url: str
    timeout_seconds: int = 30


@dataclass(frozen=True)
class DisplaySpec:
    label: str = ""
    description: str = ""


@dataclass(frozen=True)
class PluginSpec:
    name: str
    version: int
    display: DisplaySpec
    connector: ConnectorSpec
    commands: tuple[CommandSpec, ...] = ()
    query_routes: tuple[QueryRouteSpec, ...] = ()
    scope_mappings: tuple[ScopeMapping, ...] = ()
    normalizers: tuple[NormalizerSpec, ...] = ()
    tables_path: Path | None = None


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    type: str = "string"
    nullable: bool = True


@dataclass(frozen=True)
class TableSpec:
    table_name: str
    dataset_key: str
    description: str
    write_mode: str
    primary_key: tuple[str, ...]
    scope_column_names: tuple[str, ...]
    columns: dict[str, ColumnSpec]
