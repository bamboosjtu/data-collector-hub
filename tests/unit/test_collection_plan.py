"""Tests for P1: Collection Plan Service."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import time
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from src.datahub.core.plugin_loader import load_all_plugins
from src.datahub.core.registry import SchemaRegistry, load_registry_from_plugins
from src.datahub.core.services.collection_plan_service import (
    DAILY_DCP_REFRESH_STEPS,
    DCP_DAILY_UPDATE_CONFIG,
    DCP_INITIAL_FULL_LOAD_CONFIG,
    CollectionPlanError,
    CollectionPlanService,
    StartPlanRunResult,
    resolve_plan_params,
)
from src.datahub.core.services.job_service import JobResult, JobService, JobServiceError
from src.datahub.core.specs import ColumnSpec, TableSpec
from src.datahub.core.time_utils import datahub_now, datahub_today, datahub_yesterday
from src.datahub.settings import Settings
from src.datahub.storage.ddl import create_metadata_tables
from src.datahub.storage.sqlite import DataHubStore


@pytest.fixture
def db_path():
    d = tempfile.mkdtemp()
    return Path(d) / "test_collection_plan.db"


@pytest.fixture
def store(db_path):
    """Create a minimal store with schema initialized."""
    registry = SchemaRegistry(version=1, tables={}, datasets=set(), raw={})
    s = DataHubStore(str(db_path), registry)
    with s.connect() as conn:
        create_metadata_tables(conn)
    return s


@pytest.fixture
def store_with_plugins(db_path):
    """Create a store with full plugin loading (for P5/P51 tests)."""
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
    # Make _wait_for_job_terminal return immediately by default
    svc._wait_for_job_terminal = MagicMock(return_value=("succeeded", False))
    return svc


@pytest.fixture
def plan_service_with_plugins(store_with_plugins, mock_job_service):
    svc = CollectionPlanService(
        store=store_with_plugins,
        job_service=mock_job_service,
        recent_days=3,
    )
    svc._wait_for_job_terminal = MagicMock(return_value=("succeeded", False))
    return svc


def _wait_for_run(store, run_id, timeout=5.0):
    """Wait for a scheduled_run to reach terminal status."""
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        run = store.get_scheduled_run(run_id)
        if run and run["status"] in ("succeeded", "partial", "failed", "skipped"):
            return run
        time.sleep(0.1)
    return store.get_scheduled_run(run_id)


# ── DDL baseline tests ──────────────────────────────────────────


class TestScheduleDDLBaseline:
    def test_scheduled_plans_table_exists(self, store):
        with store.connect() as conn:
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
        assert "scheduled_plans" in tables
        assert "scheduled_runs" in tables
        assert "scheduled_run_steps" in tables

    def test_scheduled_plans_columns(self, store):
        with store.connect() as conn:
            cols = {r[1]: r for r in conn.execute("PRAGMA table_info(scheduled_plans)").fetchall()}
        assert "plan_name" in cols
        assert "enabled" in cols
        assert "schedule_type" in cols
        assert "schedule_time" in cols
        assert "timezone" in cols
        assert "config_json" in cols
        assert "next_run_at" in cols

    def test_scheduled_runs_columns(self, store):
        with store.connect() as conn:
            cols = {r[1]: r for r in conn.execute("PRAGMA table_info(scheduled_runs)").fetchall()}
        assert "run_id" in cols
        assert "plan_name" in cols
        assert "trigger_source" in cols
        assert "status" in cols

    def test_scheduled_run_steps_columns(self, store):
        with store.connect() as conn:
            cols = {r[1]: r for r in conn.execute("PRAGMA table_info(scheduled_run_steps)").fetchall()}
        assert "run_id" in cols
        assert "step_order" in cols
        assert "command_name" in cols
        assert "params_json" in cols
        assert "job_id" in cols
        assert "status" in cols
        assert "wait_for_terminal" in cols


# ── Seed default plan tests ─────────────────────────────────────


class TestSeedDefaultPlan:
    def test_seed_creates_daily_dcp_refresh(self, plan_service, store):
        plan_service.seed_default_plans()
        plan = store.get_scheduled_plan("daily_dcp_refresh")
        assert plan is not None
        assert plan["enabled"] == 0
        assert plan["schedule_type"] == "daily"
        assert plan["schedule_time"] == "02:00"

    def test_seed_idempotent(self, plan_service, store):
        plan_service.seed_default_plans()
        plan_service.seed_default_plans()
        plans = store.list_scheduled_plans()
        daily_plans = [p for p in plans if p["plan_name"] == "daily_dcp_refresh"]
        assert len(daily_plans) == 1

    def test_daily_dcp_refresh_has_7_steps(self, plan_service, store):
        plan_service.seed_default_plans()
        plan = store.get_scheduled_plan("daily_dcp_refresh")
        config = json.loads(plan["config_json"])
        assert len(config["steps"]) == 7


# ── run_plan_now async tests ────────────────────────────────────


class TestRunPlanNowAsync:
    def test_run_plan_now_returns_immediately(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        assert isinstance(result, StartPlanRunResult)
        assert result.status == "running"
        assert result.run_id.startswith("run_daily_dcp_refresh_")

    def test_run_plan_now_creates_steps(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        steps = store.get_scheduled_run_steps(result.run_id)
        assert len(steps) == 7

    def test_run_plan_now_background_executes_steps(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        run = _wait_for_run(store, result.run_id)
        assert mock_job_service.submit_command.call_count == 7

    def test_run_plan_now_source_passed_to_submit_command(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        result = plan_service.run_plan_now("daily_dcp_refresh", source="scheduler")
        _wait_for_run(store, result.run_id)
        for call in mock_job_service.submit_command.call_args_list:
            assert call.kwargs["source"] == "scheduler"

    def test_run_plan_now_plan_not_found(self, plan_service):
        with pytest.raises(CollectionPlanError) as exc_info:
            plan_service.run_plan_now("nonexistent_plan")
        assert exc_info.value.error_code == "plan_not_found"

    def test_run_plan_now_prevents_overlap(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # Create a running run manually
        store.create_scheduled_run(
            run_id="run_daily_dcp_refresh_existing",
            plan_name="daily_dcp_refresh",
            trigger_source="api",
            status="running",
        )
        with pytest.raises(CollectionPlanError) as exc_info:
            plan_service.run_plan_now("daily_dcp_refresh")
        assert exc_info.value.error_code == "plan_already_running"

    def test_failed_step_with_ingestion_job_id_writes_step_job_id(self, plan_service, mock_job_service, store):
        """P1.2: When submit_command raises JobServiceError with ingestion_job_id,
        the step's job_id should be written from the exception."""
        plan_service.seed_default_plans()

        def side_effect(cmd, params=None, source="api"):
            if cmd == "refresh_plan_progress":
                raise JobServiceError("external_sync_failed", "connection refused", ingestion_job_id="ing_failed_abc123")
            return JobResult(ingestion_job_id=f"ing_{cmd}_ok", status="accepted")

        mock_job_service.submit_command.side_effect = side_effect
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        run = _wait_for_run(store, result.run_id)

        steps = store.get_scheduled_run_steps(result.run_id)
        # Step 1 (refresh_plan_progress) should have job_id from exception
        assert steps[1]["job_id"] == "ing_failed_abc123"
        assert steps[1]["status"] == "failed"
        # Step 0 should have succeeded
        assert steps[0]["status"] == "succeeded"
        # Run should be failed
        assert run["status"] == "failed"

    def test_failed_step_marks_remaining_skipped(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        call_count = 0

        def side_effect(cmd, params=None, source="api"):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise JobServiceError("external_sync_failed", "connection refused")
            return JobResult(ingestion_job_id=f"ing_{cmd}_{call_count}", status="accepted")

        mock_job_service.submit_command.side_effect = side_effect
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        run = _wait_for_run(store, result.run_id)
        # Check step statuses
        steps = store.get_scheduled_run_steps(result.run_id)
        statuses = [s["status"] for s in steps]
        assert statuses[0] == "succeeded"
        assert statuses[1] == "failed"
        # Remaining steps should be skipped
        for s in statuses[2:]:
            assert s == "skipped"
        # Run should be failed
        assert run["status"] == "failed"

    def test_partial_step_continues_but_run_partial(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # Make _wait_for_job_terminal return partial for step 3, succeeded for others
        wait_results = iter([("succeeded", False), ("succeeded", False), ("partial", False), ("succeeded", False), ("succeeded", False), ("succeeded", False), ("succeeded", False)])
        plan_service._wait_for_job_terminal = MagicMock(side_effect=lambda jid, **kw: next(wait_results))

        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        run = _wait_for_run(store, result.run_id)
        assert run["status"] == "partial"

    def test_daily_meetings_uses_resolve_params(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        _wait_for_run(store, result.run_id)
        # Find the backfill_daily_meetings_by_range call
        calls = mock_job_service.submit_command.call_args_list
        meeting_call = None
        for call in calls:
            if call.args[0] == "backfill_daily_meetings_by_range":
                meeting_call = call
                break
        assert meeting_call is not None
        params = meeting_call.kwargs.get("params") or meeting_call.args[1]
        today = datahub_today().isoformat()
        assert params["startDate"] == today
        assert params["endDate"] == today
        assert params["chunk_days"] == 1


# ── next_run_at logic tests ─────────────────────────────────────


class TestNextRunAtLogic:
    def test_api_run_now_does_not_change_next_run_at(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # Set a specific next_run_at
        store.update_plan_next_run("daily_dcp_refresh", "2026-07-01 02:00:00")
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        _wait_for_run(store, result.run_id)
        plan = store.get_scheduled_plan("daily_dcp_refresh")
        # next_run_at should remain unchanged
        assert plan["next_run_at"] == "2026-07-01 02:00:00"

    def test_scheduler_run_advances_next_run_at(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        store.update_plan_next_run("daily_dcp_refresh", "2020-01-01 02:00:00")
        result = plan_service.run_plan_now("daily_dcp_refresh", source="scheduler")
        _wait_for_run(store, result.run_id)
        plan = store.get_scheduled_plan("daily_dcp_refresh")
        # next_run_at should have been advanced
        assert plan["next_run_at"] is not None
        assert plan["next_run_at"] > "2020-01-01 02:00:00"

    def test_api_run_fills_empty_next_run_at(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # next_run_at is NULL by default for seeded plans
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        _wait_for_run(store, result.run_id)
        plan = store.get_scheduled_plan("daily_dcp_refresh")
        # next_run_at should be filled since it was empty
        assert plan["next_run_at"] is not None


# ── scheduler_tick tests ────────────────────────────────────────


class TestSchedulerTick:
    def test_scheduler_disabled_does_not_trigger(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # Plan is disabled by default
        plan_service.scheduler_tick()
        mock_job_service.submit_command.assert_not_called()

    def test_scheduler_enabled_but_not_due_does_not_trigger(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # Enable plan but set next_run_at to future
        store.upsert_scheduled_plan(
            plan_name="daily_dcp_refresh",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            config_json=json.dumps({"steps": DAILY_DCP_REFRESH_STEPS}),
            next_run_at="2099-01-01 02:00:00",
        )
        plan_service.scheduler_tick()
        time.sleep(0.5)
        mock_job_service.submit_command.assert_not_called()

    def test_scheduler_enabled_and_due_triggers_run(self, plan_service, mock_job_service, store):
        plan_service.seed_default_plans()
        # Enable plan and set next_run_at to past, with single step
        store.upsert_scheduled_plan(
            plan_name="daily_dcp_refresh",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            config_json=json.dumps({"steps": [{"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True}]}),
            next_run_at="2020-01-01 02:00:00",
        )
        plan_service.scheduler_tick()
        time.sleep(1)
        mock_job_service.submit_command.assert_called_once()
        call = mock_job_service.submit_command.call_args
        assert call.kwargs["source"] == "scheduler"

    def test_scheduler_tick_is_non_blocking(self, plan_service, mock_job_service, store):
        """scheduler_tick should return quickly, not wait for run to complete."""
        plan_service.seed_default_plans()
        store.upsert_scheduled_plan(
            plan_name="daily_dcp_refresh",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            config_json=json.dumps({"steps": [{"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True}]}),
            next_run_at="2020-01-01 02:00:00",
        )
        # _wait_for_job_terminal is mocked to return immediately, so tick should be fast
        start = time.monotonic()
        plan_service.scheduler_tick()
        elapsed = time.monotonic() - start
        assert elapsed < 2.0


# ── stale run cleanup tests ─────────────────────────────────────


class TestMarkStaleRuns:
    def test_mark_stale_runs(self, plan_service, store):
        # Create a stale running run
        store.create_scheduled_run(
            run_id="run_stale_test",
            plan_name="daily_dcp_refresh",
            trigger_source="scheduler",
            status="running",
        )
        # Manually set started_at to old time
        with store.connect() as conn:
            conn.execute(
                "UPDATE scheduled_runs SET started_at = '2020-01-01 00:00:00' WHERE run_id = 'run_stale_test'"
            )
            conn.commit()
        marked = plan_service.mark_stale_runs(stale_seconds=3600)
        assert marked == 1
        run = store.get_scheduled_run("run_stale_test")
        assert run["status"] == "failed"

    def test_stale_run_does_not_block_run_now(self, plan_service, mock_job_service, store):
        """Stale running run should be cleaned up by run_plan_now, allowing a new run."""
        plan_service.seed_default_plans()
        # Create a stale running run
        store.create_scheduled_run(
            run_id="run_stale_block",
            plan_name="daily_dcp_refresh",
            trigger_source="api",
            status="running",
        )
        with store.connect() as conn:
            conn.execute(
                "UPDATE scheduled_runs SET started_at = '2020-01-01 00:00:00' WHERE run_id = 'run_stale_block'"
            )
            conn.commit()
        # run_plan_now should succeed because stale run gets cleaned up first
        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        assert result.status == "running"


# ── Store CRUD tests ────────────────────────────────────────────


class TestStoreScheduleCRUD:
    def test_upsert_and_get_plan(self, store):
        store.upsert_scheduled_plan(
            plan_name="test_plan",
            enabled=1,
            schedule_type="daily",
            schedule_time="03:00",
            config_json='{"steps": []}',
        )
        plan = store.get_scheduled_plan("test_plan")
        assert plan is not None
        assert plan["plan_name"] == "test_plan"
        assert plan["enabled"] == 1

    def test_upsert_updates_existing(self, store):
        store.upsert_scheduled_plan(
            plan_name="test_plan",
            enabled=0,
            schedule_type="daily",
            schedule_time="02:00",
            config_json='{"steps": []}',
        )
        store.upsert_scheduled_plan(
            plan_name="test_plan",
            enabled=1,
            schedule_type="daily",
            schedule_time="03:00",
            config_json='{"steps": [{"command": "x"}]}',
        )
        plan = store.get_scheduled_plan("test_plan")
        assert plan["enabled"] == 1
        assert plan["schedule_time"] == "03:00"

    def test_list_plans(self, store):
        store.upsert_scheduled_plan(plan_name="a_plan", schedule_type="daily", config_json='{}')
        store.upsert_scheduled_plan(plan_name="b_plan", schedule_type="daily", config_json='{}')
        plans = store.list_scheduled_plans()
        assert len(plans) >= 2

    def test_create_and_get_run(self, store):
        store.create_scheduled_run(run_id="run_1", plan_name="test", trigger_source="api", status="running")
        run = store.get_scheduled_run("run_1")
        assert run is not None
        assert run["trigger_source"] == "api"

    def test_list_runs_by_plan(self, store):
        store.create_scheduled_run(run_id="run_1", plan_name="plan_a", trigger_source="api", status="running")
        store.create_scheduled_run(run_id="run_2", plan_name="plan_b", trigger_source="api", status="running")
        runs = store.list_scheduled_runs(plan_name="plan_a")
        assert len(runs) == 1
        assert runs[0]["plan_name"] == "plan_a"

    def test_create_and_get_steps(self, store):
        store.create_scheduled_run(run_id="run_1", plan_name="test", trigger_source="api", status="running")
        store.create_scheduled_run_step(run_id="run_1", step_order=0, command_name="cmd_a", params_json='{}', status="pending")
        store.create_scheduled_run_step(run_id="run_1", step_order=1, command_name="cmd_b", params_json='{}', status="pending")
        steps = store.get_scheduled_run_steps("run_1")
        assert len(steps) == 2
        assert steps[0]["command_name"] == "cmd_a"

    def test_update_step_status(self, store):
        store.create_scheduled_run(run_id="run_1", plan_name="test", trigger_source="api", status="running")
        store.create_scheduled_run_step(run_id="run_1", step_order=0, command_name="cmd_a", params_json='{}', status="pending")
        steps = store.get_scheduled_run_steps("run_1")
        step_id = steps[0]["id"]
        store.update_scheduled_run_step(step_id, status="running", job_id="ing_test_123")
        updated = store.get_scheduled_run_steps("run_1")[0]
        assert updated["status"] == "running"
        assert updated["job_id"] == "ing_test_123"

    def test_get_running_plan_run(self, store):
        store.create_scheduled_run(run_id="run_1", plan_name="test", trigger_source="api", status="running")
        store.create_scheduled_run(run_id="run_2", plan_name="test", trigger_source="api", status="succeeded")
        running = store.get_running_plan_run("test")
        assert running is not None
        assert running["run_id"] == "run_1"

    def test_update_plan_last_run(self, store):
        store.upsert_scheduled_plan(plan_name="test", schedule_type="daily", config_json='{}')
        store.update_plan_last_run("test", run_id="run_1", status="succeeded", next_run_at="2026-06-15 02:00:00")
        plan = store.get_scheduled_plan("test")
        assert plan["last_run_id"] == "run_1"
        assert plan["last_status"] == "succeeded"
        assert plan["next_run_at"] == "2026-06-15 02:00:00"


# ══════════════════════════════════════════════════════════════════
# P5: Configurable DCP business collection plans
# ══════════════════════════════════════════════════════════════════


# ── 1. seed_default_plans creates dcp_initial_full_load and dcp_daily_update ──

class TestSeedDefaultPlans:

    def test_seeds_initial_full_load(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        plan = store_with_plugins.get_scheduled_plan("dcp_initial_full_load")
        assert plan is not None
        assert plan["enabled"] == 0
        assert plan["schedule_type"] == "manual"
        assert plan["schedule_time"] is None

    def test_seeds_daily_update(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        plan = store_with_plugins.get_scheduled_plan("dcp_daily_update")
        assert plan is not None
        assert plan["enabled"] == 0
        assert plan["schedule_type"] == "daily"
        assert plan["schedule_time"] == "02:00"

    def test_seeds_legacy_daily_dcp_refresh(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        plan = store_with_plugins.get_scheduled_plan("daily_dcp_refresh")
        assert plan is not None

    def test_idempotent_seed(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        plan_service_with_plugins.seed_default_plans()
        plans = store_with_plugins.list_scheduled_plans()
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

    def test_manual_plan_not_triggered(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        # Enable the manual plan and set next_run_at to past
        store_with_plugins.upsert_scheduled_plan(
            plan_name="dcp_initial_full_load",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False),
        )
        store_with_plugins.update_plan_next_run("dcp_initial_full_load", "2020-01-01 00:00:00")

        plan_service_with_plugins.scheduler_tick()

        # No run should be created for manual plan
        runs = store_with_plugins.list_scheduled_runs("dcp_initial_full_load", limit=10)
        assert len(runs) == 0


# ── 6. daily plan triggered by scheduler_tick ──

class TestDailyPlanSchedulerTrigger:

    def test_daily_plan_triggered(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        store_with_plugins.upsert_scheduled_plan(
            plan_name="dcp_daily_update",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False),
        )
        store_with_plugins.update_plan_next_run("dcp_daily_update", "2020-01-01 00:00:00")

        plan_service_with_plugins.scheduler_tick()

        runs = store_with_plugins.list_scheduled_runs("dcp_daily_update", limit=10)
        assert len(runs) >= 1
        assert runs[0]["trigger_source"] == "scheduler"


# ── 7. daily_update safety: params resolve to today/today ──

class TestDailyUpdateParamsResolution:

    def test_backfill_resolves_today_today(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        store_with_plugins.upsert_scheduled_plan(
            plan_name="dcp_daily_update",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False),
        )

        result = plan_service_with_plugins.run_plan_now("dcp_daily_update", source="api")
        run = _wait_for_run(store_with_plugins, result.run_id)

        steps = store_with_plugins.get_scheduled_run_steps(result.run_id)
        backfill_step = [s for s in steps if s["command_name"] == "backfill_daily_meetings_by_range"][0]
        params = json.loads(backfill_step["params_json"])
        today = datahub_today().isoformat()
        assert params["startDate"] == today
        assert params["endDate"] == today


# ── 8. initial_full_load safety: endDate resolves to yesterday ──

class TestInitialFullLoadParamsResolution:

    def test_backfill_resolves_yesterday(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        store_with_plugins.upsert_scheduled_plan(
            plan_name="dcp_initial_full_load",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False),
        )

        result = plan_service_with_plugins.run_plan_now("dcp_initial_full_load", source="api")
        run = _wait_for_run(store_with_plugins, result.run_id)

        steps = store_with_plugins.get_scheduled_run_steps(result.run_id)
        backfill_step = [s for s in steps if s["command_name"] == "backfill_daily_meetings_by_range"][0]
        params = json.loads(backfill_step["params_json"])
        yesterday = datahub_yesterday().isoformat()
        assert params["startDate"] == "2024-01-01"
        assert params["endDate"] == yesterday


# ── 9. all_plan_projects fan-out with years param ──

class TestAllPlanProjectsFanOut:

    def test_multi_year_queries_multiple_years(self, store_with_plugins):
        """Verify _project_fan_out with multi_year=True queries multiple years."""
        from src.datahub.core.specs import CommandSpec
        from plugins.dcp.fan_out import refresh_towers_for_all_plan_projects

        # Insert test data into dcp_plan_year_project
        with store_with_plugins.connect() as conn:
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
            "store": store_with_plugins,
            "ingestion_job_id": "ing_test_all_projects",
            "command": command,
            "plugin": plugin,
            "params": {"years": [2024, 2025]},
            "trigger_clients": {},
            "plugins": [],
            "callback_base_url": "http://localhost:8000",
        }

        # Create the parent job first
        store_with_plugins.create_ingestion_job(
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

    def test_current_year_only(self, store_with_plugins):
        """Verify _project_fan_out without multi_year only queries current year."""
        from src.datahub.core.specs import CommandSpec
        from plugins.dcp.fan_out import refresh_towers_for_current_plan_projects

        current_year = str(datahub_today().year)

        # Insert data for current year and another year
        with store_with_plugins.connect() as conn:
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
            "store": store_with_plugins,
            "ingestion_job_id": "ing_test_current_projects",
            "command": command,
            "plugin": plugin,
            "params": {},
            "trigger_clients": {},
            "plugins": [],
            "callback_base_url": "http://localhost:8000",
        }

        store_with_plugins.create_ingestion_job(
            ingestion_job_id="ing_test_current_projects",
            producer_job_id="prod_test2",
            job_type="refresh_towers_for_current_plan_projects",
            params={},
            plugin_id="dcp",
        )

        result = refresh_towers_for_current_plan_projects(ctx)

        # Only current year project
        assert result["total"] == 1


# ══════════════════════════════════════════════════════════════════
# P5.1: Long-running plan timeout configuration
# ══════════════════════════════════════════════════════════════════


# ── 1. Config has wait_timeout_seconds ──

class TestConfigTimeout:

    def test_initial_full_load_has_timeout(self):
        assert DCP_INITIAL_FULL_LOAD_CONFIG["wait_timeout_seconds"] == 28800

    def test_initial_full_load_has_poll_interval(self):
        assert DCP_INITIAL_FULL_LOAD_CONFIG["poll_interval_seconds"] == 5

    def test_daily_update_has_timeout(self):
        assert DCP_DAILY_UPDATE_CONFIG["wait_timeout_seconds"] == 7200

    def test_daily_update_has_poll_interval(self):
        assert DCP_DAILY_UPDATE_CONFIG["poll_interval_seconds"] == 5


# ── 2. Step-level timeout overrides plan-level ──

class TestStepLevelTimeout:

    def test_step_timeout_overrides_plan(self, plan_service_with_plugins, store_with_plugins, mock_job_service):
        config = {
            "wait_timeout_seconds": 3600,
            "poll_interval_seconds": 5,
            "steps": [
                {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True, "wait_timeout_seconds": 7200},
                {"command": "refresh_plan_progress", "params": {}, "wait_for_terminal": True},
            ],
        }
        store_with_plugins.upsert_scheduled_plan(
            plan_name="test_step_timeout",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(config, ensure_ascii=False),
        )

        # Track what timeout was passed to _wait_for_job_terminal
        wait_calls = []
        def track_wait(job_id, timeout=3600, poll_interval=5.0):
            wait_calls.append({"job_id": job_id, "timeout": timeout, "poll_interval": poll_interval})
            return ("succeeded", False)

        plan_service_with_plugins._wait_for_job_terminal = MagicMock(side_effect=track_wait)

        result = plan_service_with_plugins.run_plan_now("test_step_timeout", source="api")
        _wait_for_run(store_with_plugins, result.run_id)

        # Step 0 should have timeout=7200 (step-level override)
        # Step 1 should have timeout=3600 (plan-level default)
        assert len(wait_calls) == 2
        assert wait_calls[0]["timeout"] == 7200
        assert wait_calls[1]["timeout"] == 3600

    def test_plan_timeout_used_when_no_step_override(self, plan_service_with_plugins, store_with_plugins, mock_job_service):
        config = {
            "wait_timeout_seconds": 28800,
            "poll_interval_seconds": 5,
            "steps": [
                {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
            ],
        }
        store_with_plugins.upsert_scheduled_plan(
            plan_name="test_plan_timeout",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(config, ensure_ascii=False),
        )

        wait_calls = []
        def track_wait(job_id, timeout=3600, poll_interval=5.0):
            wait_calls.append({"timeout": timeout, "poll_interval": poll_interval})
            return ("succeeded", False)

        plan_service_with_plugins._wait_for_job_terminal = MagicMock(side_effect=track_wait)

        result = plan_service_with_plugins.run_plan_now("test_plan_timeout", source="api")
        _wait_for_run(store_with_plugins, result.run_id)

        assert len(wait_calls) == 1
        assert wait_calls[0]["timeout"] == 28800
        assert wait_calls[0]["poll_interval"] == 5


# ── 3. Timeout error recording ──

class TestTimeoutErrorRecording:

    def test_timeout_marks_step_failed_with_message(self, plan_service_with_plugins, store_with_plugins, mock_job_service):
        config = {
            "wait_timeout_seconds": 3600,
            "steps": [
                {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
            ],
        }
        store_with_plugins.upsert_scheduled_plan(
            plan_name="test_timeout_err",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(config, ensure_ascii=False),
        )

        # Simulate timeout
        plan_service_with_plugins._wait_for_job_terminal = MagicMock(return_value=("failed", True))

        result = plan_service_with_plugins.run_plan_now("test_timeout_err", source="api")
        run = _wait_for_run(store_with_plugins, result.run_id)

        assert run["status"] == "failed"
        assert "wait timeout" in (run["error"] or "")

        steps = store_with_plugins.get_scheduled_run_steps(result.run_id)
        assert steps[0]["status"] == "failed"
        assert "wait timeout after 3600s" in (steps[0]["error"] or "")


# ── 4. mark_stale_runs respects plan timeout ──

class TestStaleRunStrategy:

    def test_stale_runs_uses_plan_timeout(self, store_with_plugins):
        """dcp_initial_full_load with wait_timeout_seconds=28800 should have
        stale cutoff = max(32400, 28800+3600) = 32400, not 7200."""
        mock_js = MagicMock(spec=JobService)
        svc = CollectionPlanService(store=store_with_plugins, job_service=mock_js, recent_days=3)
        svc.seed_default_plans()

        # Create a running run for dcp_initial_full_load
        store_with_plugins.create_scheduled_run(
            run_id="run_stale_test",
            plan_name="dcp_initial_full_load",
            trigger_source="api",
            status="running",
        )

        # Set started_at to 4 hours ago (14400s) — should NOT be stale
        # because dcp_initial_full_load has timeout=28800, stale = max(32400, 32400) = 32400
        from datetime import timedelta as td
        four_hours_ago = (datahub_now() - td(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        with store_with_plugins.connect() as conn:
            conn.execute("UPDATE scheduled_runs SET started_at = ? WHERE run_id = ?", (four_hours_ago, "run_stale_test"))

        marked = svc.mark_stale_runs()
        assert marked == 0  # Should NOT be marked stale after 4 hours

    def test_stale_runs_marks_old_runs(self, store_with_plugins):
        """A run older than the plan's stale cutoff should be marked."""
        mock_js = MagicMock(spec=JobService)
        svc = CollectionPlanService(store=store_with_plugins, job_service=mock_js, recent_days=3)
        svc.seed_default_plans()

        store_with_plugins.create_scheduled_run(
            run_id="run_stale_old",
            plan_name="dcp_daily_update",
            trigger_source="api",
            status="running",
        )

        # Set started_at to 10 hours ago — should be stale
        # dcp_daily_update timeout=7200, stale = max(32400, 7200+3600) = 32400
        ten_hours_ago = (datahub_now() - __import__("datetime").timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S")
        with store_with_plugins.connect() as conn:
            conn.execute("UPDATE scheduled_runs SET started_at = ? WHERE run_id = ?", (ten_hours_ago, "run_stale_old"))

        # With default stale_seconds=32400, 10 hours = 36000s > 32400
        marked = svc.mark_stale_runs(stale_seconds=32400)
        assert marked == 1

    def test_default_stale_seconds_is_32400(self):
        """Verify the default stale_seconds changed from 7200 to 32400."""
        import inspect
        sig = inspect.signature(CollectionPlanService.mark_stale_runs)
        assert sig.parameters["stale_seconds"].default == 32400


# ── 5. Existing daily/manual tests don't regress ──

class TestP51NoRegression:

    def test_daily_plan_still_works(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        store_with_plugins.upsert_scheduled_plan(
            plan_name="dcp_daily_update",
            enabled=1,
            schedule_type="daily",
            schedule_time="02:00",
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False),
        )
        result = plan_service_with_plugins.run_plan_now("dcp_daily_update", source="api")
        run = _wait_for_run(store_with_plugins, result.run_id)
        assert run["status"] == "succeeded"

    def test_manual_plan_still_works(self, plan_service_with_plugins, store_with_plugins):
        plan_service_with_plugins.seed_default_plans()
        store_with_plugins.upsert_scheduled_plan(
            plan_name="dcp_initial_full_load",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False),
        )
        result = plan_service_with_plugins.run_plan_now("dcp_initial_full_load", source="api")
        run = _wait_for_run(store_with_plugins, result.run_id)
        assert run["status"] == "succeeded"
