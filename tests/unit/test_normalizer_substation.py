"""Tests for dcp_project_substation normalizer."""
import pytest

from plugins.dcp.normalizers import normalize_substation


class TestNormalizeSubstation:
    """Test normalize_substation filters wrapper-only rows and strips wrapper fields."""

    def _call(self, rows):
        return normalize_substation("dcp_project_substation", {"singleProjectCode": "P1"}, rows)

    def test_normal_row_passes(self):
        """Normal substation row with all business fields passes through."""
        rows = [{"singleProjectCode": "P1", "id": "S1", "prjCode": "PRJ1",
                 "longitude": "116.4", "latitude": "39.9",
                 "longitudeLook": "116.4001", "latitudeLook": "39.9001"}]
        result = self._call(rows)
        assert len(result) == 1
        assert result[0]["table_name"] == "dcp_project_substation"
        assert len(result[0]["rows"]) == 1
        out = result[0]["rows"][0]
        assert out["singleProjectCode"] == "P1"
        assert out["id"] == "S1"
        assert out["longitude"] == "116.4"

    def test_id_null_but_coordinates_present(self):
        """id=None but longitude/latitude have values — allowed."""
        rows = [{"singleProjectCode": "P1", "id": None, "prjCode": None,
                 "longitude": "116.4", "latitude": "39.9",
                 "longitudeLook": None, "latitudeLook": None}]
        result = self._call(rows)
        assert len(result[0]["rows"]) == 1
        out = result[0]["rows"][0]
        assert "id" not in out  # None values not included
        assert out["longitude"] == "116.4"

    def test_id_null_but_prjcode_present(self):
        """id=None but prjCode has value — allowed."""
        rows = [{"singleProjectCode": "P1", "id": None, "prjCode": "PRJ1",
                 "longitude": None, "latitude": None}]
        result = self._call(rows)
        assert len(result[0]["rows"]) == 1
        assert result[0]["rows"][0]["prjCode"] == "PRJ1"

    def test_wrapper_only_data_null_skipped(self):
        """Wrapper-only row with data=null is skipped entirely."""
        rows = [{"singleProjectCode": "P1", "id": None, "prjCode": None,
                 "longitude": None, "latitude": None,
                 "longitudeLook": None, "latitudeLook": None,
                 "code": "200", "data": None, "message": "操作成功",
                 "success": True, "traceId": ""}]
        result = self._call(rows)
        assert len(result[0]["rows"]) == 0

    def test_wrapper_fields_not_in_output(self):
        """Wrapper fields (code/message/success/traceId/data) never appear in output."""
        rows = [{"singleProjectCode": "P1", "id": "S1",
                 "code": "200", "message": "ok", "success": True,
                 "traceId": "abc", "data": {"id": "S1"}}]
        result = self._call(rows)
        out = result[0]["rows"][0]
        for field in ("code", "message", "success", "traceId", "data", "extra"):
            assert field not in out, f"wrapper field '{field}' should not be in output"

    def test_business_fields_but_missing_singleprojectcode_passes(self):
        """Row with business fields but no singleProjectCode passes through
        so validator can catch the missing primary key."""
        rows = [{"id": "S1", "prjCode": "PRJ1", "longitude": "116.4",
                 "latitude": "39.9"}]
        result = self._call(rows)
        assert len(result[0]["rows"]) == 1
        out = result[0]["rows"][0]
        assert "singleProjectCode" not in out
        assert out["id"] == "S1"

    def test_all_business_null_scope_only_skipped(self):
        """Row with only singleProjectCode (scope) and all business fields null — skipped."""
        rows = [{"singleProjectCode": "P1", "id": None, "prjCode": None,
                 "longitude": None, "latitude": None,
                 "longitudeLook": None, "latitudeLook": None}]
        result = self._call(rows)
        assert len(result[0]["rows"]) == 0

    def test_mixed_rows(self):
        """Mix of valid and wrapper-only rows — only valid ones pass."""
        rows = [
            {"singleProjectCode": "P1", "id": "S1", "prjCode": "PRJ1",
             "longitude": "116.4", "latitude": "39.9"},
            {"singleProjectCode": "P2", "id": None, "prjCode": None,
             "longitude": None, "latitude": None,
             "code": "200", "data": None, "message": "操作成功"},
            {"singleProjectCode": "P3", "id": None, "prjCode": "PRJ3",
             "longitude": None, "latitude": None},
        ]
        result = self._call(rows)
        assert len(result[0]["rows"]) == 2
        codes = [r.get("singleProjectCode") for r in result[0]["rows"]]
        assert "P1" in codes
        assert "P3" in codes
        assert "P2" not in codes

    def test_no_recursion_same_source_target(self):
        """Normalizer outputs dcp_project_substation as target — same name as source.
        The core _apply_normalizers does single-pass, so no recursion."""
        rows = [{"singleProjectCode": "P1", "id": "S1"}]
        result = self._call(rows)
        assert result[0]["table_name"] == "dcp_project_substation"
