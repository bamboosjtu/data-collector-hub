"""Tests for P5: Configurable DCP business collection plans."""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.datahub.core.registry import SchemaRegistry
from src.datahub.core.services.collection_plan_service import (
    DCP_DAILY_UPDATE_CONFIG,
    DCP_INITIAL_FULL_LOAD_CONFIG,
    CollectionPlanError,
    CollectionPlanService,
    resolve_plan_params,
)
from src.datahub.core.services.job_service import JobResult, JobService
from src.datahub.core.time_utils import datahub_today, datahub_yesterday
from src.datahub.storage.ddl import create_metadata_tables
from src.datahub.storage.sqlite import DataHubStore


@pytest.fixture
def db_path():
    d = tempfile.mkdtemp()
    return Path(d) / "test_p5.db"


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


@pytest.fixture
def mock_job_service():
    svc = MagicMock(spec=JobService)
    svc.submit_command.return_value = JobResult(
        ingestion_job_id="ing_test_cmd_abc123",
        status="accepted",
        downloader_job_id="job_test_abc123",
    )
    return svc


@pytest.fixture
def plan_service(store, mock_job_service):
    svc = CollectionPlanService(
        store=store,
        job_service=mock_job_service,
        recent_days=3,
    )
    svc._wait_for_job_terminal = MagicMock(return_value="succeeded")
    return svc


def _wait_for_run(store, run_id, timeout=5.0):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        run = store.get_scheduled_run(run_id)
        if run and run["status"] in ("succeeded", "partial", "failed", "skipped"):
            return run
        time.sleep(0.1)
    return store.get_scheduled_run(run_id)


# ── 1. seed_default_plans creates dcp_initial_full_load and dcp_daily_update ──

class TestSeedDefaultPlans:

    def test_seeds_initial_full_load(self, plan_service, store):
        plan_service.seed_default_plans()
        plan = store.get_scheduled_plan("dcp_initial_full_load")
        assert plan is not None
        assert plan["enabled"] == 0
        assert plan["schedule_type"] == "manual"
        assert plan["schedule_time"] is None

    def test_seeds_daily_update(self, plan_service, store):
        plan_service.seed_default_plans()
        plan = store.get_scheduled_plan("dcp_daily_update")
        assert plan is not None
        assert plan["enabled"] == 0
        assert plan["schedule_type"] == "daily"
        assert plan["schedule_time"] == "02:00"

    def test_seeds_legacy_daily_dcp_refresh(self, plan_service, store):
        plan_service.seed_default_plans()
        plan = store.get_scheduled_plan("daily_dcp_refresh")
        assert plan is not None

    def test_idempotent_seed(self, plan_service, store):
        plan_service.seed_default_plans()
        plan_service.seed_default_plans()
        plans = store.list_scheduled_plans()
        names = [p["plan_name"] for p in plans]
        assert names.count("dcp_initial_full_load") == 1
        assert names.count("dcp_daily_update") == 1


# ── 2. dcp_initial_full_load config ──

class TestInitialFullLoadConfig:

    def test_manual_schedule_type(self):
        assert DCP_INITIAL_FULL_LOAD_CONFIG["steps"]
        # The plan uses all_plan_projects commands
        step_names = [s["command"] for s in DCP_INITIAL_FULL_LOAD_CONFIG["steps"]]
        assert "refresh_towers_for_all_plan_projects" in step_names
        assert "refresh_substations_for_all_plan_projects" in step_names
        assert "refresh_line_sections_for_all_plan_projects" in step_names

    def test_backfill_enddate_is_yesterday_placeholder(self):
        backfill_step = [s for s in DCP_INITIAL_FULL_LOAD_CONFIG["steps"]
                         if s["command"] == "backfill_daily_meetings_by_range"][0]
        assert backfill_step["params"]["endDate"] == "$yesterday"
        assert backfill_step["params"]["startDate"] == "2024-01-01"


# ── 3. dcp_daily_update config ──

class TestDailyUpdateConfig:

    def test_daily_schedule_type(self):
        assert DCP_DAILY_UPDATE_CONFIG["steps"]
        step_names = [s["command"] for s in DCP_DAILY_UPDATE_CONFIG["steps"]]
        # Uses current_plan_projects, not all_plan_projects
        assert "refresh_towers_for_current_plan_projects" in step_names
        assert "refresh_towers_for_all_plan_projects" not in step_names

    def test_backfill_dates_are_today_placeholder(self):
        backfill_step = [s for s in DCP_DAILY_UPDATE_CONFIG["steps"]
                         if s["command"] == "backfill_daily_meetings_by_range"][0]
        assert backfill_step["params"]["startDate"] == "$today"
        assert backfill_step["params"]["endDate"] == "$today"


# ── 4. resolve_plan_params ──

class TestResolvePlanParams:

    def test_resolve_today(self):
        today = datahub_today().isoformat()
        assert resolve_plan_params("$today") == today

    def test_resolve_yesterday(self):
        yesterday = datahub_yesterday().isoformat()
        assert resolve_plan_params("$yesterday") == yesterday

    def test_resolve_current_year(self):
        year = str(datahub_today().year)
        assert resolve_plan_params("$current_year") == year

    def test_resolve_in_dict(self):
        result = resolve_plan_params({"startDate": "$today", "endDate": "$yesterday"})
        assert result["startDate"] == datahub_today().isoformat()
        assert result["endDate"] == datahub_yesterday().isoformat()

    def test_resolve_in_list(self):
        result = resolve_plan_params(["$today", "$yesterday"])
        assert result[0] == datahub_today().isoformat()
        assert result[1] == datahub_yesterday().isoformat()

    def test_plain_string_unchanged(self):
        assert resolve_plan_params("2024-01-01") == "2024-01-01"
        assert resolve_plan_params("hello") == "hello"

    def test_non_string_unchanged(self):
        assert resolve_plan_params(42) == 42
        assert resolve_plan_params(3.14) == 3.14
        assert resolve_plan_params(True) is True

    def test_nested_dict_and_list(self):
        result = resolve_plan_params({
            "years": [2024, 2025, 2026],
            "startDate": "$today",
            "nested": {"key": "$yesterday"},
        })
        assert result["years"] == [2024, 2025, 2026]
        assert result["startDate"] == datahub_today().isoformat()
        assert result["nested"]["key"] == datahub_yesterday().isoformat()


# ── 5. manual plan not auto-triggered by scheduler_tick ──

class TestManualPlanSchedulerSkip:

    def test_manual_plan_not_triggered(self, plan_service, store):
        plan_service.seed_default_plans()
        # Enable the manual plan and set next_run_at to past
        store.upsert_scheduled_plan(
            plan_name="dcp_initial_full_load",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False),
        )
        store.update_plan_next_run("dcp_initial_full_load", "2020-01-01 00:00:00")

        plan_service.scheduler_tick()

        # No run should be created for manual plan
        runs = store.list_scheduled_runs("dcp_initial_full_load", limit=10)
        assert len(runs) == 0


# ── 6. daily plan triggered by scheduler_tick ──

class TestDailyPlanSchedulerTrigger:

    def test_daily_plan_triggered(self, plan_service, store):
        plan_service.seed_default_plans()
        store.upsert_scheduled_plan(
            plan_name="dcp_daily_update",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False),
        )
        store.update_plan_next_run("dcp_daily_update", "2020-01-01 00:00:00")

        plan_service.scheduler_tick()

        runs = store.list_scheduled_runs("dcp_daily_update", limit=10)
        assert len(runs) >= 1
        assert runs[0]["trigger_source"] == "scheduler"


# ── 7. daily_update safety: params resolve to today/today ──

class TestDailyUpdateParamsResolution:

    def test_backfill_resolves_today_today(self, plan_service, store):
        plan_service.seed_default_plans()
        store.upsert_scheduled_plan(
            plan_name="dcp_daily_update",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False),
        )

        result = plan_service.run_plan_now("dcp_daily_update", source="api")
        run = _wait_for_run(store, result.run_id)

        steps = store.get_scheduled_run_steps(result.run_id)
        backfill_step = [s for s in steps if s["command_name"] == "backfill_daily_meetings_by_range"][0]
        params = json.loads(backfill_step["params_json"])
        today = datahub_today().isoformat()
        assert params["startDate"] == today
        assert params["endDate"] == today


# ── 8. initial_full_load safety: endDate resolves to yesterday ──

class TestInitialFullLoadParamsResolution:

    def test_backfill_resolves_yesterday(self, plan_service, store):
        plan_service.seed_default_plans()
        store.upsert_scheduled_plan(
            plan_name="dcp_initial_full_load",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False),
        )

        result = plan_service.run_plan_now("dcp_initial_full_load", source="api")
        run = _wait_for_run(store, result.run_id)

        steps = store.get_scheduled_run_steps(result.run_id)
        backfill_step = [s for s in steps if s["command_name"] == "backfill_daily_meetings_by_range"][0]
        params = json.loads(backfill_step["params_json"])
        yesterday = datahub_yesterday().isoformat()
        assert params["startDate"] == "2024-01-01"
        assert params["endDate"] == yesterday


# ── 9. all_plan_projects fan-out with years param ──

class TestAllPlanProjectsFanOut:

    def test_multi_year_queries_multiple_years(self, store):
        """Verify _project_fan_out with multi_year=True queries multiple years."""
        from src.datahub.core.specs import CommandSpec
        from plugins.dcp.fan_out import refresh_towers_for_all_plan_projects

        # Insert test data into dcp_plan_year_project
        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "P001", "Project A"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "P002", "Project B"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2025", "P001", "Project A"))

        # Build a mock context
        command = CommandSpec(
            name="refresh_towers_for_all_plan_projects",
            description="test",
            required_params=(),
            trigger={"type": "plugin_handler", "handler": "dcp.fan_out:refresh_towers_for_all_plan_projects"},
            max_concurrency=5,
            max_concurrency_limit=5,
            cooldown_seconds=3,
        )
        plugin = MagicMock()
        plugin.name = "dcp"

        ctx = {
            "store": store,
            "ingestion_job_id": "ing_test_all_projects",
            "command": command,
            "plugin": plugin,
            "params": {"years": [2024, 2025]},
            "trigger_clients": {},
            "plugins": [],
            "callback_base_url": "http://localhost:8000",
        }

        # Create the parent job first
        store.create_ingestion_job(
            ingestion_job_id="ing_test_all_projects",
            producer_job_id="prod_test",
            job_type="refresh_towers_for_all_plan_projects",
            params={"years": [2024, 2025]},
            plugin_id="dcp",
        )

        result = refresh_towers_for_all_plan_projects(ctx)

        # Should have deduplicated P001 across years
        assert result["total"] == 2  # P001 and P002


# ── 10. current_plan_projects still only queries current year ──

class TestCurrentPlanProjectsNoRegression:

    def test_current_year_only(self, store):
        """Verify _project_fan_out without multi_year only queries current year."""
        from src.datahub.core.specs import CommandSpec
        from plugins.dcp.fan_out import refresh_towers_for_current_plan_projects

        current_year = str(datahub_today().year)

        # Insert data for current year and another year
        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", (current_year, "P001", "Project A"))
            conn.execute("INSERT INTO dcp_plan_year_project (year, prjCode, prjName) VALUES (?, ?, ?)", ("2024", "P002", "Project B"))

        command = CommandSpec(
            name="refresh_towers_for_current_plan_projects",
            description="test",
            required_params=(),
            trigger={"type": "plugin_handler", "handler": "dcp.fan_out:refresh_towers_for_current_plan_projects"},
            max_concurrency=5,
            max_concurrency_limit=5,
            cooldown_seconds=3,
        )
        plugin = MagicMock()
        plugin.name = "dcp"

        ctx = {
            "store": store,
            "ingestion_job_id": "ing_test_current_projects",
            "command": command,
            "plugin": plugin,
            "params": {},
            "trigger_clients": {},
            "plugins": [],
            "callback_base_url": "http://localhost:8000",
        }

        store.create_ingestion_job(
            ingestion_job_id="ing_test_current_projects",
            producer_job_id="prod_test2",
            job_type="refresh_towers_for_current_plan_projects",
            params={},
            plugin_id="dcp",
        )

        result = refresh_towers_for_current_plan_projects(ctx)

        # Only current year project
        assert result["total"] == 1
