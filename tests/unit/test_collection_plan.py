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

from src.datahub.core.registry import SchemaRegistry
from src.datahub.core.services.collection_plan_service import (
    DAILY_DCP_REFRESH_STEPS,
    CollectionPlanError,
    CollectionPlanService,
    StartPlanRunResult,
)
from src.datahub.core.services.job_service import JobResult, JobService, JobServiceError
from src.datahub.core.specs import ColumnSpec, TableSpec
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
    svc._wait_for_job_terminal = MagicMock(return_value="succeeded")
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
        wait_results = iter(["succeeded", "succeeded", "partial", "succeeded", "succeeded", "succeeded", "succeeded"])
        plan_service._wait_for_job_terminal = MagicMock(side_effect=lambda jid: next(wait_results))

        result = plan_service.run_plan_now("daily_dcp_refresh", source="api")
        run = _wait_for_run(store, result.run_id)
        assert run["status"] == "partial"

    def test_daily_meetings_uses_recent_days(self, plan_service, mock_job_service, store):
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
        from datetime import date, timedelta
        today = date.today()
        expected_start = (today - timedelta(days=3)).isoformat()
        assert params["startDate"] == expected_start
        assert params["endDate"] == today.isoformat()
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
