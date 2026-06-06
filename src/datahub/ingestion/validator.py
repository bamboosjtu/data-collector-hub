from __future__ import annotations

import logging
from typing import Any

from src.datahub.core.registry import SchemaRegistry, validate_row, validate_scope

logger = logging.getLogger(__name__)


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
        raw_rows = table_payload.get("rows") or []
        valid_rows = []
        for row in raw_rows:
            try:
                valid_rows.append(validate_row(table, dict(row)))
            except ValueError as exc:
                logger.warning("skipping row in %s: %s", table.table_name, exc)
        if valid_rows:
            validated.append((table, scope_values, valid_rows))
    return validated
