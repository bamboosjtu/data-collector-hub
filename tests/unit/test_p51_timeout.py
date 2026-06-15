"""Tests for P5.1: Long-running plan timeout configuration."""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.datahub.core.plugin_loader import load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.core.services.collection_plan_service import (
    DCP_DAILY_UPDATE_CONFIG,
    DCP_INITIAL_FULL_LOAD_CONFIG,
    CollectionPlanService,
)
from src.datahub.core.services.job_service import JobResult, JobService
from src.datahub.core.time_utils import datahub_now, datahub_today
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore


@pytest.fixture
def db_path():
    d = tempfile.mkdtemp()
    return Path(d) / "test_p51.db"


@pytest.fixture
def store(db_path):
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
    svc._wait_for_job_terminal = MagicMock(return_value=("succeeded", False))
    return svc


def _wait_for_run(store, run_id, timeout=5.0):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        run = store.get_scheduled_run(run_id)
        if run and run["status"] in ("succeeded", "partial", "failed", "skipped"):
            return run
        time.sleep(0.1)
    return store.get_scheduled_run(run_id)


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

    def test_step_timeout_overrides_plan(self, plan_service, store, mock_job_service):
        config = {
            "wait_timeout_seconds": 3600,
            "poll_interval_seconds": 5,
            "steps": [
                {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True, "wait_timeout_seconds": 7200},
                {"command": "refresh_plan_progress", "params": {}, "wait_for_terminal": True},
            ],
        }
        store.upsert_scheduled_plan(
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

        plan_service._wait_for_job_terminal = MagicMock(side_effect=track_wait)

        result = plan_service.run_plan_now("test_step_timeout", source="api")
        _wait_for_run(store, result.run_id)

        # Step 0 should have timeout=7200 (step-level override)
        # Step 1 should have timeout=3600 (plan-level default)
        assert len(wait_calls) == 2
        assert wait_calls[0]["timeout"] == 7200
        assert wait_calls[1]["timeout"] == 3600

    def test_plan_timeout_used_when_no_step_override(self, plan_service, store, mock_job_service):
        config = {
            "wait_timeout_seconds": 28800,
            "poll_interval_seconds": 5,
            "steps": [
                {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
            ],
        }
        store.upsert_scheduled_plan(
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

        plan_service._wait_for_job_terminal = MagicMock(side_effect=track_wait)

        result = plan_service.run_plan_now("test_plan_timeout", source="api")
        _wait_for_run(store, result.run_id)

        assert len(wait_calls) == 1
        assert wait_calls[0]["timeout"] == 28800
        assert wait_calls[0]["poll_interval"] == 5


# ── 3. Timeout error recording ──

class TestTimeoutErrorRecording:

    def test_timeout_marks_step_failed_with_message(self, plan_service, store, mock_job_service):
        config = {
            "wait_timeout_seconds": 3600,
            "steps": [
                {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
            ],
        }
        store.upsert_scheduled_plan(
            plan_name="test_timeout_err",
            enabled=1,
            schedule_type="manual",
            schedule_time=None,
            timezone="Asia/Shanghai",
            config_json=json.dumps(config, ensure_ascii=False),
        )

        # Simulate timeout
        plan_service._wait_for_job_terminal = MagicMock(return_value=("failed", True))

        result = plan_service.run_plan_now("test_timeout_err", source="api")
        run = _wait_for_run(store, result.run_id)

        assert run["status"] == "failed"
        assert "wait timeout" in (run["error"] or "")

        steps = store.get_scheduled_run_steps(result.run_id)
        assert steps[0]["status"] == "failed"
        assert "wait timeout after 3600s" in (steps[0]["error"] or "")


# ── 4. mark_stale_runs respects plan timeout ──

class TestStaleRunStrategy:

    def test_stale_runs_uses_plan_timeout(self, store):
        """dcp_initial_full_load with wait_timeout_seconds=28800 should have
        stale cutoff = max(32400, 28800+3600) = 32400, not 7200."""
        mock_js = MagicMock(spec=JobService)
        svc = CollectionPlanService(store=store, job_service=mock_js, recent_days=3)
        svc.seed_default_plans()

        # Create a running run for dcp_initial_full_load
        store.create_scheduled_run(
            run_id="run_stale_test",
            plan_name="dcp_initial_full_load",
            trigger_source="api",
            status="running",
        )

        # Set started_at to 4 hours ago (14400s) — should NOT be stale
        # because dcp_initial_full_load has timeout=28800, stale = max(32400, 32400) = 32400
        from datetime import timedelta as td
        four_hours_ago = (datahub_now() - td(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        with store.connect() as conn:
            conn.execute("UPDATE scheduled_runs SET started_at = ? WHERE run_id = ?", (four_hours_ago, "run_stale_test"))

        marked = svc.mark_stale_runs()
        assert marked == 0  # Should NOT be marked stale after 4 hours

    def test_stale_runs_marks_old_runs(self, store):
        """A run older than the plan's stale cutoff should be marked."""
        mock_js = MagicMock(spec=JobService)
        svc = CollectionPlanService(store=store, job_service=mock_js, recent_days=3)
        svc.seed_default_plans()

        store.create_scheduled_run(
            run_id="run_stale_old",
            plan_name="dcp_daily_update",
            trigger_source="api",
            status="running",
        )

        # Set started_at to 10 hours ago — should be stale
        # dcp_daily_update timeout=7200, stale = max(32400, 7200+3600) = 32400
        ten_hours_ago = (datahub_now() - __import__("datetime").timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S")
        with store.connect() as conn:
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

class TestNoRegression:

    def test_daily_plan_still_works(self, plan_service, store):
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
        assert run["status"] == "succeeded"

    def test_manual_plan_still_works(self, plan_service, store):
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
        assert run["status"] == "succeeded"
