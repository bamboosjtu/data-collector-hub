"""Tests for normalize_daily_meeting normalizer."""
import pytest
from plugins.dcp.normalizers import normalize_daily_meeting


def _make_row(**kwargs):
    return kwargs


class TestNormalizeDailyMeeting:
    def test_normal_row_passes(self):
        row = _make_row(
            date="2026-06-07", id="abc123",
            prjName="Test Project", prjCode="P001",
            biddingSectionCode="B001", singleProjectCode="SP001",
            leaderName="Zhang San", workSiteName="Site A",
            voltageLevel="500kV", provinceCode="43",
        )
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        assert len(result) == 1
        assert result[0]["table_name"] == "dcp_safe_daily_meeting"
        assert len(result[0]["rows"]) == 1
        out = result[0]["rows"][0]
        assert out["date"] == "2026-06-07"
        assert out["id"] == "abc123"
        assert out["prjName"] == "Test Project"
        assert out["biddingSectionCode"] == "B001"
        assert out["leaderName"] == "Zhang San"

    def test_wrapper_fields_not_in_output(self):
        row = _make_row(
            date="2026-06-07", id="abc123",
            code=200, message="ok", success=True,
            traceId="trace-123", data=None,
            prjName="Test",
        )
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        out = result[0]["rows"][0]
        assert "code" not in out
        assert "message" not in out
        assert "success" not in out
        assert "traceId" not in out
        assert "data" not in out
        assert "extra" not in out

    def test_date_from_scope_values(self):
        row = _make_row(id="abc123", prjName="Test")
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {"date": "2026-06-07"}, [row])
        out = result[0]["rows"][0]
        assert out["date"] == "2026-06-07"

    def test_missing_date_and_id_skipped(self):
        row = _make_row(prjName="Test", biddingSectionCode="B001")
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        assert len(result[0]["rows"]) == 0

    def test_missing_id_skipped(self):
        row = _make_row(date="2026-06-07", prjName="Test")
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        assert len(result[0]["rows"]) == 0

    def test_missing_date_skipped(self):
        row = _make_row(id="abc123", prjName="Test")
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        assert len(result[0]["rows"]) == 0

    def test_snapshot_table_name_preserved(self):
        row = _make_row(date="2026-06-07", id="abc123", prjName="Test")
        result = normalize_daily_meeting("dcp_safe_daily_meeting_snapshot", {}, [row])
        assert result[0]["table_name"] == "dcp_safe_daily_meeting_snapshot"

    def test_integer_fields_preserved(self):
        row = _make_row(
            date="2026-06-07", id="abc123",
            currentConstrHeadcount=10,
            constructionHeadcount=20,
            cameraNum=3,
        )
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        out = result[0]["rows"][0]
        assert out["currentConstrHeadcount"] == 10
        assert out["constructionHeadcount"] == 20
        assert out["cameraNum"] == 3

    def test_json_field_preserved(self):
        row = _make_row(
            date="2026-06-07", id="abc123",
            dailyMeetingFileList=[{"name": "file1.pdf"}],
        )
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        out = result[0]["rows"][0]
        assert out["dailyMeetingFileList"] == [{"name": "file1.pdf"}]

    def test_mixed_rows(self):
        rows = [
            _make_row(date="2026-06-07", id="1", prjName="A"),
            _make_row(date="2026-06-07", prjName="B"),  # missing id
            _make_row(date="2026-06-07", id="3", prjName="C", code=200, message="ok"),
        ]
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, rows)
        output_rows = result[0]["rows"]
        assert len(output_rows) == 2
        assert output_rows[0]["prjName"] == "A"
        assert output_rows[1]["prjName"] == "C"
        assert "code" not in output_rows[1]

    def test_no_recursion_same_source_target(self):
        """Same source_table -> target should not cause recursion."""
        row = _make_row(date="2026-06-07", id="abc123", prjName="Test")
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        assert result[0]["table_name"] == "dcp_safe_daily_meeting"
        assert len(result[0]["rows"]) == 1

    def test_undeclared_fields_not_in_output(self):
        """Fields not in the declared schema should not appear in output."""
        row = _make_row(
            date="2026-06-07", id="abc123",
            prjName="Test",
            someRandomField="should not appear",
            anotherUnknownField=42,
        )
        result = normalize_daily_meeting("dcp_safe_daily_meeting", {}, [row])
        out = result[0]["rows"][0]
        assert "someRandomField" not in out
        assert "anotherUnknownField" not in out
