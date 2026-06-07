from __future__ import annotations

import logging
from typing import Any

from src.datahub.core.registry import SchemaRegistry, TableSpec, validate_row, validate_scope

logger = logging.getLogger(__name__)

# Known API response wrapper fields from DCP downloader.
# A row containing most of these is likely an empty wrapper, not real business data.
_API_WRAPPER_FIELDS = frozenset({"code", "message", "success", "traceId"})

# Fields that indicate real business payload — if any of these are non-empty,
# the row is NOT an empty wrapper even if it has API wrapper fields.
_PAYLOAD_FIELDS = frozenset({"raw", "data", "result", "payload", "response"})


def _is_empty_wrapper_row(table: TableSpec, row: dict[str, Any], exc: ValueError) -> bool:
    """Determine if a row is an empty API wrapper that should be skipped.

    Criteria (all must be true):
    1. The ValueError is specifically about missing primary key or missing required field.
    2. The row contains at least 3 of the known API wrapper fields.
    3. All primary key columns have None values in the row.
    4. No payload fields (raw/data/result/payload/response) have non-empty values.
    5. No declared business columns (other than scope columns) have non-None values.
    """
    msg = str(exc)
    is_pk_or_required_error = (
        msg.startswith("missing_primary_key:") or
        (msg.startswith("schema_mismatch:") and "is required" in msg)
    )
    if not is_pk_or_required_error:
        return False

    wrapper_overlap = len(_API_WRAPPER_FIELDS.intersection(row))
    if wrapper_overlap < 3:
        return False

    # All primary key values must be None/missing
    for pk in table.primary_key:
        val = row.get(pk)
        if val is not None:
            return False

    # Payload fields must be empty — non-empty means real data
    for field in _PAYLOAD_FIELDS:
        val = row.get(field)
        if val is not None and val != "" and val != [] and val != {}:
            return False

    # No declared business columns (excluding scope and extra) should have values
    scope_cols = set(table.scope_column_names)
    for col_name in table.columns:
        if col_name == "extra" or col_name in scope_cols:
            continue
        if col_name in _API_WRAPPER_FIELDS:
            continue
        val = row.get(col_name)
        if val is not None:
            return False

    return True


class SkippedRow:
    """Record of a skipped row with reason."""

    __slots__ = ("table_name", "reason", "row_preview")

    def __init__(self, table_name: str, reason: str, row: dict[str, Any]) -> None:
        self.table_name = table_name
        self.reason = reason
        # Only keep keys for preview, not full values (may contain large data)
        self.row_preview = {k: (v if not isinstance(v, (dict, list)) else f"<{type(v).__name__}>") for k, v in row.items()}

    def to_dict(self) -> dict[str, Any]:
        return {"table_name": self.table_name, "reason": self.reason, "row_keys": list(self.row_preview.keys())}


def validate_payload(
    registry: SchemaRegistry, payload: dict[str, Any], apply_scope_mappings
) -> tuple[list[tuple[Any, dict[str, Any], list[dict[str, Any]]]], list[SkippedRow]]:
    """Validate a table-batch payload.

    Returns a tuple of (validated_tables, skipped_rows).
    - validated_tables: list of (table, scope_values, rows) for writing.
    - skipped_rows: list of SkippedRow records for empty wrapper rows that were skipped.
    """
    dataset_key = str(payload["dataset_key"])
    registry.require_dataset(dataset_key)
    tables = payload.get("tables")
    if not isinstance(tables, list) or not tables:
        raise ValueError("invalid_batch: tables must be a non-empty list")
    validated = []
    skipped: list[SkippedRow] = []
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
            row_dict = dict(row)
            try:
                valid_rows.append(validate_row(table, row_dict))
            except ValueError as exc:
                if _is_empty_wrapper_row(table, row_dict, exc):
                    reason = str(exc).split(":", 1)[0].strip()
                    skipped.append(SkippedRow(table.table_name, reason, row_dict))
                    logger.warning(
                        "skipping empty wrapper row in %s: %s row_keys=%s",
                        table.table_name, exc, sorted(row_dict.keys()),
                    )
                else:
                    raise
        if valid_rows:
            validated.append((table, scope_values, valid_rows))
    return validated, skipped
