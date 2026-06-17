"""Tests for P5.2: Explicit projectCode dedup in multi-year fan-out."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.datahub.core.specs import CommandSpec
from src.datahub.core.time_utils import datahub_today
from src.datahub.storage.sqlite import DataHubStore


@pytest.fixture
def db_path():
    d = tempfile.mkdtemp()
    return Path(d) / "test_p52.db"


@pytest.fixture
def store(db_path):
    from src.datahub.core.plugin_loader import load_all_plugins
    from src.datahub.core.registry import load_registry_from_plugins
    from src.datahub.settings import Settings
    plugins = load_all_plugins(Settings.plugin_dir)
    registry = load_registry_from_plugins(plugins)
    s = DataHubStore(str(db_path), registry)
    s.init_schema(dev_mode=True)
    return s


def _make_command(name="refresh_towers_for_all_plan_projects"):
    return CommandSpec(
        name=name,
        description="test",
        required_params=(),
        trigger={"type": "plugin_handler", "handler": f"dcp.fan_out:{name}"},
        max_concurrency=5,
        max_concurrency_limit=5,
        cooldown_seconds=3,
    )


def _make_ctx(store, job_id, command, params=None):
    plugin = MagicMock()
    plugin.name = "dcp"
    return {
        "store": store,
        "ingestion_job_id": job_id,
        "command": command,
        "plugin": plugin,
        "params": params or {},
        "trigger_clients": {},
        "plugins": [],
        "callback_base_url": "http://localhost:8000",
    }


def _create_parent_job(store, job_id, command_name, params=None):
    store.create_ingestion_job(
        ingestion_job_id=job_id,
        producer_job_id=f"prod_{job_id}",
        job_type=command_name,
        params=params or {},
        plugin_id="dcp",
    )


# ── Case 1: multi_year dedup ──

class TestMultiYearDedup:

    def test_dedup_across_years(self, store):
        """Same projectCode across 2024/2025/2026 should produce only one child."""
        from plugins.dcp.fan_out import refresh_towers_for_all_plan_projects

        # 2024: A, B | 2025: A, C | 2026: A
        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "A", "Proj A"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "B", "Proj B"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "A", "Proj A"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "C", "Proj C"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2026", "A", "Proj A"))

        command = _make_command()
        job_id = "ing_p52_dedup"
        _create_parent_job(store, job_id, "refresh_towers_for_all_plan_projects", {"years": [2024, 2025, 2026]})
        ctx = _make_ctx(store, job_id, command, {"years": [2024, 2025, 2026]})

        result = refresh_towers_for_all_plan_projects(ctx)

        # 3 unique projects: A, B, C
        assert result["total"] == 3
        assert result["unique_projects"] == 3
        assert result["source_rows"] == 5
        assert result["duplicate_project_rows"] == 2  # A appears 2 extra times
        assert result["skipped_empty_project_code"] == 0

        # Verify fanout_items contain exactly 3 items with correct projectCode
        items = store.list_fanout_items_with_child_jobs(job_id)
        param_sets = [item["params_json"] for item in items]
        codes = set()
        import json
        for p in param_sets:
            parsed = json.loads(p)
            codes.add(parsed["projectCode"])
        assert codes == {"A", "B", "C"}


# ── Case 2: empty projectCode skip ──

class TestEmptyProjectCodeSkip:

    def test_none_empty_whitespace_skipped(self, store):
        """prjCode=None, "", or whitespace should be skipped."""
        from plugins.dcp.fan_out import refresh_towers_for_all_plan_projects

        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "VALID1", "Valid 1"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "", "Empty"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "   ", "Whitespace"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "VALID2", "Valid 2"))

        command = _make_command()
        job_id = "ing_p52_empty"
        _create_parent_job(store, job_id, "refresh_towers_for_all_plan_projects", {"years": [2024]})
        ctx = _make_ctx(store, job_id, command, {"years": [2024]})

        result = refresh_towers_for_all_plan_projects(ctx)

        assert result["total"] == 2
        assert result["unique_projects"] == 2
        assert result["source_rows"] == 4
        assert result["skipped_empty_project_code"] == 2
        assert result["duplicate_project_rows"] == 0


# ── Case 3: control params not in child params ──

class TestControlParamsExcluded:

    def test_control_params_not_in_child(self, store):
        """years/max_concurrency/max_items/cooldown_seconds must not appear in child params."""
        from plugins.dcp.fan_out import refresh_towers_for_all_plan_projects

        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "P001", "Project 1"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "P002", "Project 2"))

        command = _make_command()
        job_id = "ing_p52_control"
        params_with_controls = {
            "years": [2024, 2025],
            "max_concurrency": 3,
            "max_items": 100,
            "cooldown_seconds": 5,
            "consecutive_failure_threshold": 10,
        }
        _create_parent_job(store, job_id, "refresh_towers_for_all_plan_projects", params_with_controls)
        ctx = _make_ctx(store, job_id, command, params_with_controls)

        result = refresh_towers_for_all_plan_projects(ctx)

        assert result["total"] == 2

        # Verify child params only contain projectCode
        items = store.list_fanout_items_with_child_jobs(job_id)
        import json
        for item in items:
            parsed = json.loads(item["params_json"])
            assert "projectCode" in parsed
            assert "years" not in parsed
            assert "max_concurrency" not in parsed
            assert "max_items" not in parsed
            assert "cooldown_seconds" not in parsed
            assert "consecutive_failure_threshold" not in parsed


# ── Case 4: current_year fan-out still dedup ──

class TestCurrentYearDedup:

    def test_current_year_dedup(self, store):
        """multi_year=False still deduplicates by projectCode within current year.

        Since dcp_plan_year_project has UNIQUE(year, prjCode), duplicates only
        appear across years. With multi_year=False, we only query current year,
        so there can't be same-year duplicates. But the dedup logic must still
        work correctly — we test that it produces the right stats.
        """
        from plugins.dcp.fan_out import refresh_towers_for_current_plan_projects

        current_year = str(datahub_today().year)

        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", (current_year, "P001", "Proj A"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", (current_year, "P002", "Proj B"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", (current_year, "P003", "Proj C"))

        command = _make_command("refresh_towers_for_current_plan_projects")
        job_id = "ing_p52_current_dedup"
        _create_parent_job(store, job_id, "refresh_towers_for_current_plan_projects")
        ctx = _make_ctx(store, job_id, command, {})

        result = refresh_towers_for_current_plan_projects(ctx)

        assert result["total"] == 3
        assert result["unique_projects"] == 3
        assert result["source_rows"] == 3
        assert result["duplicate_project_rows"] == 0
        assert result["skipped_empty_project_code"] == 0


# ── Case 5: statistics fields present in result ──

class TestStatisticsFields:

    def test_all_stats_present(self, store):
        """Verify all required statistics fields are in the result."""
        from plugins.dcp.fan_out import refresh_towers_for_all_plan_projects

        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "X1", "X1"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "X1", "X1 dup"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "X2", "X2"))

        command = _make_command()
        job_id = "ing_p52_stats"
        _create_parent_job(store, job_id, "refresh_towers_for_all_plan_projects", {"years": [2024, 2025]})
        ctx = _make_ctx(store, job_id, command, {"years": [2024, 2025]})

        result = refresh_towers_for_all_plan_projects(ctx)

        # Required fields
        assert "fanout_scheduler" in result
        assert result["fanout_scheduler"] is True
        assert "total" in result
        assert "source_rows" in result
        assert "unique_projects" in result
        assert "duplicate_project_rows" in result
        assert "skipped_empty_project_code" in result
        assert "years" in result
        assert "max_concurrency" in result

        # Values
        assert result["source_rows"] == 3
        assert result["unique_projects"] == 2
        assert result["duplicate_project_rows"] == 1
        assert result["skipped_empty_project_code"] == 0
        assert result["years"] == ["2024", "2025"]
        assert result["max_concurrency"] == 5
