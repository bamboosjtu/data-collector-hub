from __future__ import annotations

from typing import Any

from src.datahub.core.registry import SchemaRegistry, validate_row, validate_scope


def validate_payload(registry: SchemaRegistry, payload: dict[str, Any], apply_scope_mappings) -> list[tuple[Any, dict[str, Any], list[dict[str, Any]]]]:
    dataset_key = str(payload["dataset_key"])
    registry.require_dataset(dataset_key)
    tables = payload.get("tables")
    if not isinstance(tables, list) or not tables:
        raise ValueError("invalid_batch: tables must be a non-empty list")
    validated = []
    for table_payload in tables:
        table = registry.require_table(str(table_payload.get("table_name")))
        if table.dataset_key != dataset_key:
            raise ValueError(f"table_dataset_mismatch: {table.table_name} belongs to {table.dataset_key}, not {dataset_key}")
        scope_values = dict(table_payload.get("scope_values") or {})
        scope_values = apply_scope_mappings(table.table_name, scope_values)
        validate_scope(table, scope_values)
        rows = [validate_row(table, dict(row)) for row in (table_payload.get("rows") or [])]
        validated.append((table, scope_values, rows))
    return validated
