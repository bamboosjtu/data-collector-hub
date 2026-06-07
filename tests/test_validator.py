"""Tests for ingestion validator: empty wrapper row skipping and strict validation."""

from __future__ import annotations

import pytest

from src.datahub.core.registry import SchemaRegistry, TableSpec, ColumnSpec
from src.datahub.ingestion.validator import _is_empty_wrapper_row, validate_payload, SkippedRow


def _make_table(name: str = "test_table", pk: tuple[str, ...] = ("id",), extra: bool = True) -> TableSpec:
    columns = {
        "id": ColumnSpec(name="id", type="string", nullable=False),
        "name": ColumnSpec(name="name", type="string", nullable=True),
        "scope_col": ColumnSpec(name="scope_col", type="string", nullable=False),
    }
    if extra:
        columns["extra"] = ColumnSpec(name="extra", type="json", nullable=True)
    return TableSpec(
        table_name=name,
        dataset_key="test_dataset",
        description="test",
        write_mode="upsert",
        primary_key=pk,
        scope_column_names=("scope_col",),
        columns=columns,
    )


def _make_registry(table: TableSpec | None = None, extra: bool | None = None) -> SchemaRegistry:
    if table is None:
        table = _make_table(extra=extra if extra is not None else True)
    return SchemaRegistry(
        version=1,
        tables={table.table_name: table},
        datasets={table.dataset_key},
        raw={"version": 1, "tables": {table.table_name: {}}},
    )


def _noop_scope_mappings(table_name: str, scope_values: dict) -> dict:
    return scope_values


# --- _is_empty_wrapper_row tests ---

class TestIsEmptyWrapperRow:
    def test_empty_wrapper_with_api_fields_and_missing_pk(self):
        """Row with API wrapper fields and no primary key → is empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": "", "scope_col": "s1"}
        exc = ValueError("missing_primary_key: test_table.id primary key is required")
        assert _is_empty_wrapper_row(table, row, exc) is True

    def test_empty_wrapper_with_required_field_error(self):
        """Row with API wrapper fields and missing required field → is empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": ""}
        exc = ValueError("schema_mismatch: test_table.scope_col is required")
        assert _is_empty_wrapper_row(table, row, exc) is True

    def test_real_business_row_missing_pk_not_skipped(self):
        """Row with real business data but missing pk → NOT empty wrapper (no API fields)."""
        table = _make_table()
        row = {"name": "real_data", "scope_col": "s1"}
        exc = ValueError("missing_primary_key: test_table.id primary key is required")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_row_with_pk_and_api_fields_not_skipped(self):
        """Row with API fields but has a primary key → NOT empty wrapper."""
        table = _make_table()
        row = {"id": "abc123", "code": "200", "message": "ok", "success": True, "traceId": "", "scope_col": "s1"}
        exc = ValueError("schema_mismatch: test_table.name is required")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_unknown_columns_error_not_skipped(self):
        """Unknown columns error → NOT empty wrapper (different error type)."""
        table = _make_table()
        row = {"id": "abc", "scope_col": "s1", "unknown_col": "val"}
        exc = ValueError("schema_mismatch: unknown columns in test_table: unknown_col")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_type_mismatch_error_not_skipped(self):
        """Type mismatch error → NOT empty wrapper."""
        table = _make_table()
        row = {"id": "abc", "scope_col": "s1", "name": 123}
        exc = ValueError("schema_mismatch: test_table.name must be string")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_only_two_api_fields_not_skipped(self):
        """Row with only 2 API wrapper fields (< 3 threshold) → NOT empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "scope_col": "s1"}
        exc = ValueError("missing_primary_key: test_table.id primary key is required")
        assert _is_empty_wrapper_row(table, row, exc) is False


# --- validate_payload integration tests ---

class TestValidatePayload:
    def test_empty_wrapper_row_is_skipped(self):
        """Empty wrapper rows are skipped and recorded."""
        registry = _make_registry()
        payload = {
            "dataset_key": "test_dataset",
            "tables": [{
                "table_name": "test_table",
                "scope_values": {"scope_col": "s1"},
                "rows": [
                    # Normal row
                    {"id": "r1", "name": "real", "scope_col": "s1"},
                    # Empty wrapper row
                    {"code": "200", "message": "ok", "success": True, "traceId": "", "scope_col": "s1"},
                ],
            }],
        }
        validated, skipped = validate_payload(registry, payload, _noop_scope_mappings)
        assert len(validated) == 1
        assert len(validated[0][2]) == 1  # only 1 valid row
        assert validated[0][2][0]["id"] == "r1"
        assert len(skipped) == 1
        assert skipped[0].table_name == "test_table"
        assert "schema_mismatch" in skipped[0].reason

    def test_real_business_row_missing_pk_raises(self):
        """A real business row missing primary key must raise, not be silently skipped."""
        registry = _make_registry()
        payload = {
            "dataset_key": "test_dataset",
            "tables": [{
                "table_name": "test_table",
                "scope_values": {"scope_col": "s1"},
                "rows": [
                    {"name": "real_data_no_id", "scope_col": "s1"},
                ],
            }],
        }
        with pytest.raises(ValueError, match="schema_mismatch.*id is required"):
            validate_payload(registry, payload, _noop_scope_mappings)

    def test_unknown_columns_raises(self):
        """Unknown columns must raise, not be silently skipped."""
        registry = _make_registry(extra=False)  # no extra column
        payload = {
            "dataset_key": "test_dataset",
            "tables": [{
                "table_name": "test_table",
                "scope_values": {"scope_col": "s1"},
                "rows": [
                    {"id": "r1", "name": "real", "scope_col": "s1", "mystery_col": "x"},
                ],
            }],
        }
        with pytest.raises(ValueError, match="schema_mismatch"):
            validate_payload(registry, payload, _noop_scope_mappings)

    def test_all_rows_empty_wrapper_returns_empty_validated(self):
        """When all rows are empty wrappers, validated is empty (no tables to write)."""
        registry = _make_registry()
        payload = {
            "dataset_key": "test_dataset",
            "tables": [{
                "table_name": "test_table",
                "scope_values": {"scope_col": "s1"},
                "rows": [
                    {"code": "200", "message": "ok", "success": True, "traceId": "", "scope_col": "s1"},
                ],
            }],
        }
        validated, skipped = validate_payload(registry, payload, _noop_scope_mappings)
        assert len(validated) == 0
        assert len(skipped) == 1

    def test_mixed_valid_and_wrapper_rows(self):
        """Mix of valid and wrapper rows: only valid rows pass, wrappers recorded."""
        registry = _make_registry()
        payload = {
            "dataset_key": "test_dataset",
            "tables": [{
                "table_name": "test_table",
                "scope_values": {"scope_col": "s1"},
                "rows": [
                    {"id": "r1", "name": "first", "scope_col": "s1"},
                    {"code": "200", "message": "ok", "success": True, "traceId": "", "scope_col": "s1"},
                    {"id": "r2", "name": "second", "scope_col": "s1"},
                ],
            }],
        }
        validated, skipped = validate_payload(registry, payload, _noop_scope_mappings)
        assert len(validated) == 1
        assert len(validated[0][2]) == 2
        assert len(skipped) == 1
