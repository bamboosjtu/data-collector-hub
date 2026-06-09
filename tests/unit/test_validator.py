"""Tests for ingestion validator: empty wrapper row skipping, strict validation, and extra field rules."""

from __future__ import annotations

import pytest

from src.datahub.core.registry import SchemaRegistry, TableSpec, ColumnSpec, validate_row
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

    def test_row_with_nonempty_data_not_skipped(self):
        """Row with non-empty 'data' field → NOT empty wrapper (has real payload)."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": "", "data": [{"id": "x"}]}
        exc = ValueError("missing_primary_key: test_table.id primary key is required")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_row_with_nonempty_result_not_skipped(self):
        """Row with non-empty 'result' field → NOT empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": "", "result": "some_data"}
        exc = ValueError("schema_mismatch: test_table.id is required")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_row_with_nonempty_raw_not_skipped(self):
        """Row with non-empty 'raw' field → NOT empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": "", "raw": {"id": "x"}}
        exc = ValueError("missing_primary_key: test_table.id primary key is required")
        assert _is_empty_wrapper_row(table, row, exc) is False

    def test_row_with_empty_data_list_is_wrapper(self):
        """Row with data=[] (empty list) → still empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": "", "data": []}
        exc = ValueError("missing_primary_key: test_table.id primary key is required")
        assert _is_empty_wrapper_row(table, row, exc) is True

    def test_row_with_business_field_value_not_skipped(self):
        """Row with a declared business column having non-None value → NOT empty wrapper."""
        table = _make_table()
        row = {"code": "200", "message": "ok", "success": True, "traceId": "", "name": "real_value"}
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


# --- extra field rules tests ---

class TestExtraFieldRules:
    def test_extra_only_contains_undeclared_fields(self):
        """extra should only contain fields not declared in the table schema."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "undeclared_field": "value1"}
        result = validate_row(table, row)
        assert result["extra"] is not None
        assert "undeclared_field" in result["extra"]
        assert result["extra"]["undeclared_field"] == "value1"

    def test_extra_does_not_contain_raw(self):
        """raw must not be stored in extra — it's an API envelope field."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "raw": {"full": "response"}}
        result = validate_row(table, row)
        assert result["extra"] is None or "raw" not in result["extra"]

    def test_extra_does_not_contain_response(self):
        """response must not be stored in extra."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "response": "full_response_body"}
        result = validate_row(table, row)
        assert result["extra"] is None or "response" not in result["extra"]

    def test_extra_does_not_contain_result(self):
        """result must not be stored in extra."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "result": {"data": []}}
        result = validate_row(table, row)
        assert result["extra"] is None or "result" not in result["extra"]

    def test_extra_does_not_contain_payload(self):
        """payload must not be stored in extra."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "payload": "big_payload"}
        result = validate_row(table, row)
        assert result["extra"] is None or "payload" not in result["extra"]

    def test_extra_does_not_duplicate_declared_fields(self):
        """Declared fields must not appear in extra — they go into normalized columns."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "extra": {"id": "dup_id", "name": "dup_name", "new_key": "val"}}
        result = validate_row(table, row)
        assert "id" not in result["extra"]
        assert "name" not in result["extra"]
        assert "new_key" in result["extra"]

    def test_extra_raw_forbidden_key(self):
        """extra.raw is a forbidden key in extra."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1", "extra": {"extra.raw": "should_be_removed", "ok_field": "val"}}
        result = validate_row(table, row)
        assert "extra.raw" not in result["extra"]
        assert "ok_field" in result["extra"]

    def test_no_extra_column_unknown_fields_rejected(self):
        """Without extra column, unknown fields cause an error."""
        table = _make_table(extra=False)
        row = {"id": "r1", "name": "test", "scope_col": "s1", "unknown_field": "val"}
        with pytest.raises(ValueError, match="schema_mismatch"):
            validate_row(table, row)

    def test_extra_is_none_when_no_overflow(self):
        """extra is None when there are no overflow fields."""
        table = _make_table()
        row = {"id": "r1", "name": "test", "scope_col": "s1"}
        result = validate_row(table, row)
        assert result["extra"] is None


# --- dcp_substation schema tests ---

class TestSubstationSchema:
    """Tests for dcp_substation: id nullable, singleProjectCode as sole primary key."""

    @staticmethod
    def _make_substation_table() -> TableSpec:
        columns = {
            "singleProjectCode": ColumnSpec(name="singleProjectCode", type="string", nullable=False),
            "id": ColumnSpec(name="id", type="string", nullable=True),
            "prjCode": ColumnSpec(name="prjCode", type="string", nullable=True),
            "longitude": ColumnSpec(name="longitude", type="string", nullable=True),
            "latitude": ColumnSpec(name="latitude", type="string", nullable=True),
            "longitudeLook": ColumnSpec(name="longitudeLook", type="string", nullable=True),
            "latitudeLook": ColumnSpec(name="latitudeLook", type="string", nullable=True),
            "extra": ColumnSpec(name="extra", type="json", nullable=True),
        }
        return TableSpec(
            table_name="dcp_substation",
            dataset_key="substation",
            description="test substation",
            write_mode="upsert",
            primary_key=("singleProjectCode",),
            scope_column_names=("singleProjectCode",),
            columns=columns,
        )

    def test_substation_with_id_succeeds(self):
        """Substation with both id and singleProjectCode -> normal入库."""
        table = self._make_substation_table()
        row = {"singleProjectCode": "SP001", "id": "sub_123", "prjCode": "P001", "longitude": "116.4", "latitude": "39.9"}
        result = validate_row(table, row)
        assert result["singleProjectCode"] == "SP001"
        assert result["id"] == "sub_123"

    def test_substation_without_id_succeeds(self):
        """Substation without id but with singleProjectCode -> normal入库."""
        table = self._make_substation_table()
        row = {"singleProjectCode": "SP001", "prjCode": "P001", "longitude": "116.4", "latitude": "39.9"}
        result = validate_row(table, row)
        assert result["singleProjectCode"] == "SP001"
        assert result["id"] is None

    def test_substation_missing_singleProjectCode_fails(self):
        """Substation without singleProjectCode -> must fail."""
        table = self._make_substation_table()
        row = {"id": "sub_123", "prjCode": "P001", "longitude": "116.4", "latitude": "39.9"}
        with pytest.raises(ValueError, match="schema_mismatch.*singleProjectCode is required"):
            validate_row(table, row)

    def test_substation_empty_singleProjectCode_fails(self):
        """Substation with empty singleProjectCode (None) -> must fail."""
        table = self._make_substation_table()
        row = {"singleProjectCode": None, "id": "sub_123"}
        with pytest.raises(ValueError, match="schema_mismatch.*singleProjectCode is required"):
            validate_row(table, row)
