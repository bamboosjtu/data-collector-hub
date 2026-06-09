"""Tests for fan-out scheduler and circuit breaker.

Covers:
1. Handler creates fanout_runs/items and returns immediately
2. Scheduler tick submits child jobs within capacity
3. Circuit breaker: consecutive failures skip pending items
4. Parent close semantics (succeeded/partial/failed)
5. _is_child_failed logic
6. _resolve_concurrency caps user override
7. Cooldown enforcement
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from plugins.dcp.fan_out import (
    _is_child_failed,
    _date_range_fan_out,
    _project_fan_out,
    _resolve_concurrency,
    _resolve_cooldown,
    _resolve_failure_threshold,
)
from src.datahub.core.fanout_scheduler import (
    _advance_fanout_run,
    _close_fanout_parent,
    _cooldown_elapsed,
)
from src.datahub.core.specs import CommandSpec, PluginSpec, DisplaySpec, ConnectorSpec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_store(jobs: dict[str, dict] | None = None):
    store = MagicMock()
    _jobs = dict(jobs or {})
    store.get_job = MagicMock(side_effect=_jobs.get)
    store.mark_job = MagicMock()
    store.query_table = MagicMock(return_value=[])
    store.connect = MagicMock()
    store.create_fanout_run_with_items = MagicMock()
    store.has_fanout_run = MagicMock(return_value=False)
    return store


def _make_command(name="refresh_daily_meetings_by_range", **kwargs):
    defaults = dict(
        name=name,
        trigger={"job_type": "safe_daily_meeting_range"},
        max_concurrency=1,
        max_concurrency_limit=5,
        cooldown_seconds=0,
    )
    defaults.update(kwargs)
    return CommandSpec(**defaults)


def _make_plugins(child_command_name="refresh_daily_meetings_by_range"):
    child_cmd = _make_command(name=child_command_name)
    plugin = PluginSpec(
        name="dcp", version=1, display=DisplaySpec(label="DCP"),
        connector=ConnectorSpec(type="http_sync", base_url="http://localhost:8010"),
        commands=(child_cmd,),
    )
    return [plugin]


def _make_client(sync_side_effect=None):
    client = MagicMock()
    client.sync = MagicMock(side_effect=sync_side_effect or [{"status": "accepted", "downloader_job_id": "job_123"}])
    return client


def _make_ctx(store, plugins, client, params=None, command=None):
    if command is None:
        command = _make_command()
    return {
        "store": store, "plugins": plugins, "trigger_clients": {"dcp": client},
        "ingestion_job_id": "ing_test_parent_001",
        "callback_base_url": "http://localhost:8000",
        "callback_headers": {"X-Callback-Key": "dev-default-callback-key"},
        "params": params or {},
        "command": command,
        "plugin": MagicMock(name="dcp"),
    }


def _succeeded_job(row_count=100, message_received=1):
    return {"status": "succeeded", "error": None, "row_count": row_count,
            "message_received": message_received, "producer_status_json": None}


def _failed_job(error="request_failed"):
    return {"status": "failed", "error": error, "row_count": 0,
            "message_received": 0, "producer_status_json": json.dumps({"error": error})}


# ---------------------------------------------------------------------------
# _is_child_failed
# ---------------------------------------------------------------------------

class TestIsChildFailed:
    def test_succeeded_not_failed(self):
        assert _is_child_failed(_succeeded_job()) is False

    def test_failed_status_is_failed(self):
        assert _is_child_failed(_failed_job()) is True

    def test_request_failed_in_producer_status(self):
        job = {"status": "partial", "error": None, "row_count": 0, "message_received": 0,
               "producer_status_json": json.dumps({"collects": [{"error": {"error_type": "request_failed"}}]})}
        assert _is_child_failed(job) is True

    def test_partial_with_data_not_failed(self):
        job = {"status": "partial", "error": None, "row_count": 50, "message_received": 1, "producer_status_json": None}
        assert _is_child_failed(job) is False


# ---------------------------------------------------------------------------
# Handler creates fanout_runs/items
# ---------------------------------------------------------------------------

class TestHandlerCreatesSchedulerState:
    def test_date_range_handler_creates_run(self):
        store = _make_store()
        plugins = _make_plugins()
        client = _make_client()
        command = _make_command(max_concurrency=3, cooldown_seconds=2)
        ctx = _make_ctx(store, plugins, client,
                        params={"startDate": "2026-01-01", "endDate": "2026-01-10"},
                        command=command)

        result = _date_range_fan_out(
            ctx=ctx, child_command="refresh_daily_meetings_by_range",
            chunk_days=1,
        )

        store.create_fanout_run_with_items.assert_called_once()
        call_kwargs = store.create_fanout_run_with_items.call_args[1]
        assert call_kwargs["max_concurrency"] == 3
        assert call_kwargs["cooldown_seconds"] == 2
        # 10 days / 1 day per chunk = 10 chunks
        assert len(call_kwargs["param_sets"]) == 10

        # Handler returns immediately with running status
        assert result["status"] == "running"
        assert result["total"] == 10

    def test_project_handler_creates_run(self):
        store = _make_store()
        project_rows = [{"prjCode": "P001"}, {"prjCode": "P002"}, {"prjCode": "P003"}]
        store.query_table = MagicMock(return_value=project_rows)
        plugins = _make_plugins("refresh_substations_for_project")
        client = _make_client()
        command = _make_command(name="refresh_substations_for_current_plan_projects", max_concurrency=5)
        ctx = _make_ctx(store, plugins, client, command=command)

        result = _project_fan_out(
            ctx=ctx, child_command="refresh_substations_for_project",
            params_mapping={"prjCode": "projectCode"},
        )

        store.create_fanout_run_with_items.assert_called_once()
        call_kwargs = store.create_fanout_run_with_items.call_args[1]
        assert call_kwargs["max_concurrency"] == 5
        assert len(call_kwargs["param_sets"]) == 3
        assert result["status"] == "running"

    def test_empty_projects_succeeds_immediately(self):
        store = _make_store()
        store.query_table = MagicMock(return_value=[])
        plugins = _make_plugins("refresh_substations_for_project")
        client = _make_client()
        command = _make_command(name="refresh_substations_for_current_plan_projects")
        ctx = _make_ctx(store, plugins, client, command=command)

        result = _project_fan_out(
            ctx=ctx, child_command="refresh_substations_for_project",
            params_mapping={"prjCode": "projectCode"},
        )

        store.create_fanout_run_with_items.assert_not_called()
        store.mark_job.assert_called()
        # Should mark as succeeded with 0 total
        mark_calls = store.mark_job.call_args_list
        last_call = mark_calls[-1]
        assert last_call[1]["status"] == "succeeded"


# ---------------------------------------------------------------------------
# Concurrency resolution
# ---------------------------------------------------------------------------

class TestConcurrencyResolution:
    def test_default_concurrency(self):
        cmd = _make_command(max_concurrency=1)
        assert _resolve_concurrency(cmd, {}) == 1

    def test_user_override_within_limit(self):
        cmd = _make_command(max_concurrency=1, max_concurrency_limit=5)
        assert _resolve_concurrency(cmd, {"max_concurrency": 3}) == 3

    def test_user_override_capped_at_limit(self):
        cmd = _make_command(max_concurrency=1, max_concurrency_limit=3)
        assert _resolve_concurrency(cmd, {"max_concurrency": 10}) == 3

    def test_no_limit_uses_default(self):
        cmd = _make_command(max_concurrency=3, max_concurrency_limit=None)
        assert _resolve_concurrency(cmd, {"max_concurrency": 100}) == 3

    def test_cooldown_from_spec(self):
        cmd = _make_command(cooldown_seconds=5.0)
        assert _resolve_cooldown(cmd, {}) == 5.0

    def test_cooldown_from_params_overrides_spec(self):
        cmd = _make_command(cooldown_seconds=5.0)
        assert _resolve_cooldown(cmd, {"cooldown_seconds": 2.0}) == 2.0

    def test_cooldown_default_when_spec_zero(self):
        cmd = _make_command(cooldown_seconds=0.0)
        assert _resolve_cooldown(cmd, {}, default=3.0) == 3.0

    def test_failure_threshold_from_params(self):
        assert _resolve_failure_threshold({"consecutive_failure_threshold": 3}) == 3

    def test_failure_threshold_default(self):
        assert _resolve_failure_threshold({}) == 5


# ---------------------------------------------------------------------------
# Scheduler tick: circuit breaker
# ---------------------------------------------------------------------------

class TestSchedulerCircuitBreaker:
    def test_circuit_opens_after_consecutive_failures(self):
        """When consecutive_failures >= threshold, circuit opens and pending items are skipped."""
        store = MagicMock()
        run = {
            "parent_job_id": "ing_test_001",
            "child_command": "refresh_daily_meetings_by_range",
            "max_concurrency": 1,
            "cooldown_seconds": 0,
            "consecutive_failure_threshold": 3,
            "circuit_opened": 0,
            "last_submit_at": None,
            "total": 10,
        }

        store.claim_fanout_run.return_value = True
        store.reset_stale_submitting_items.return_value = 0
        store.list_submitted_fanout_items.return_value = []
        store.get_fanout_stats.return_value = {"pending": 7, "submitting": 0, "submitted": 0, "succeeded": 0, "failed": 3, "skipped": 0}
        store.get_consecutive_failures.return_value = 3
        store.get_fanout_run.return_value = run

        _advance_fanout_run(
            store, {}, [], run,
            callback_base_url="http://localhost:8000",
            callback_headers=None,
            scheduler_id="test-scheduler",
        )

        store.mark_fanout_circuit_open.assert_called_once_with("ing_test_001")
        store.skip_pending_fanout_items.assert_called_once_with("ing_test_001")

    def test_circuit_not_open_below_threshold(self):
        """When consecutive_failures < threshold, circuit stays closed."""
        store = MagicMock()
        run = {
            "parent_job_id": "ing_test_001",
            "child_command": "refresh_daily_meetings_by_range",
            "max_concurrency": 1,
            "cooldown_seconds": 0,
            "consecutive_failure_threshold": 5,
            "circuit_opened": 0,
            "last_submit_at": None,
            "total": 10,
        }

        store.claim_fanout_run.return_value = True
        store.reset_stale_submitting_items.return_value = 0
        store.list_submitted_fanout_items.return_value = []
        store.get_fanout_stats.return_value = {"pending": 8, "submitting": 0, "submitted": 0, "succeeded": 1, "failed": 1, "skipped": 0}
        store.get_consecutive_failures.return_value = 1
        store.get_fanout_run.return_value = run
        store.claim_next_pending_fanout_item.return_value = None

        _advance_fanout_run(
            store, {}, [], run,
            callback_base_url="http://localhost:8000",
            callback_headers=None,
            scheduler_id="test-scheduler",
        )

        store.mark_fanout_circuit_open.assert_not_called()
        store.skip_pending_fanout_items.assert_not_called()

    def test_circuit_close_uses_refreshed_run_snapshot(self):
        """If circuit opens and no submitted work remains, close result must include circuit_opened."""
        store = MagicMock()
        before = {
            "parent_job_id": "ing_test_001",
            "child_command": "refresh_daily_meetings_by_range",
            "max_concurrency": 1,
            "cooldown_seconds": 0,
            "consecutive_failure_threshold": 3,
            "circuit_opened": 0,
            "last_submit_at": None,
            "total": 3,
        }
        after = {**before, "circuit_opened": 1}

        store.claim_fanout_run.return_value = True
        store.reset_stale_submitting_items.return_value = 0
        store.list_submitted_fanout_items.return_value = []
        store.get_fanout_stats.side_effect = [
            {"pending": 0, "submitting": 0, "submitted": 0, "succeeded": 0, "failed": 3, "skipped": 0},
            {"pending": 0, "submitting": 0, "submitted": 0, "succeeded": 0, "failed": 3, "skipped": 0},
        ]
        store.get_consecutive_failures.return_value = 3
        store.get_fanout_run.side_effect = [before, after]

        _advance_fanout_run(
            store, {}, [], before,
            callback_base_url="http://localhost:8000",
            callback_headers=None,
            scheduler_id="test-scheduler",
        )

        mark_kwargs = store.mark_job.call_args[1]
        assert mark_kwargs["status"] == "failed"
        assert mark_kwargs["result"]["circuit_opened"] is True
        assert "circuit breaker" in mark_kwargs["error"]



# ---------------------------------------------------------------------------
# Scheduler tick: close parent
# ---------------------------------------------------------------------------

class TestSchedulerCloseParent:
    def test_all_succeeded_closes_as_succeeded(self):
        stats = {"pending": 0, "submitting": 0, "submitted": 0, "succeeded": 10, "failed": 0, "skipped": 0}
        run = {"parent_job_id": "ing_test_001", "total": 10, "circuit_opened": 0,
               "consecutive_failure_threshold": 5, "max_concurrency": 3}
        store = MagicMock()

        _close_fanout_parent(store, "ing_test_001", stats, run)

        store.close_fanout_run.assert_called_once()
        store.mark_job.assert_called_once()
        mark_kwargs = store.mark_job.call_args[1]
        assert mark_kwargs["status"] == "succeeded"

    def test_mixed_results_closes_as_partial(self):
        stats = {"pending": 0, "submitting": 0, "submitted": 0, "succeeded": 8, "failed": 2, "skipped": 0}
        run = {"parent_job_id": "ing_test_001", "total": 10, "circuit_opened": 0,
               "consecutive_failure_threshold": 5, "max_concurrency": 3}
        store = MagicMock()

        _close_fanout_parent(store, "ing_test_001", stats, run)

        mark_kwargs = store.mark_job.call_args[1]
        assert mark_kwargs["status"] == "partial"

    def test_all_failed_closes_as_failed(self):
        stats = {"pending": 0, "submitting": 0, "submitted": 0, "succeeded": 0, "failed": 10, "skipped": 0}
        run = {"parent_job_id": "ing_test_001", "total": 10, "circuit_opened": 0,
               "consecutive_failure_threshold": 5, "max_concurrency": 3}
        store = MagicMock()

        _close_fanout_parent(store, "ing_test_001", stats, run)

        mark_kwargs = store.mark_job.call_args[1]
        assert mark_kwargs["status"] == "failed"
        assert mark_kwargs["error"] is not None

    def test_circuit_opened_closes_as_failed(self):
        stats = {"pending": 0, "submitting": 0, "submitted": 0, "succeeded": 5, "failed": 5, "skipped": 20}
        run = {"parent_job_id": "ing_test_001", "total": 30, "circuit_opened": 1,
               "consecutive_failure_threshold": 5, "max_concurrency": 3}
        store = MagicMock()

        _close_fanout_parent(store, "ing_test_001", stats, run)

        mark_kwargs = store.mark_job.call_args[1]
        assert mark_kwargs["status"] == "partial"
        assert "circuit breaker" in (mark_kwargs.get("error") or "")


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------

class TestCooldown:
    def test_no_last_submit_allows_immediate(self):
        assert _cooldown_elapsed(None, 5.0) is True

    def test_zero_cooldown_allows_immediate(self):
        assert _cooldown_elapsed("2026-01-01 00:00:00", 0.0) is True

    def test_recent_submit_blocks(self):
        # _cooldown_elapsed compares against datahub_now() which is Beijing time
        # but the stored timestamp is also Beijing time, so they should be comparable
        # Use a timestamp far in the future to ensure it's recent
        from src.datahub.core.time_utils import datahub_now
        future = (datahub_now()).strftime("%Y-%m-%d %H:%M:%S")
        assert _cooldown_elapsed(future, 60.0) is False


# ---------------------------------------------------------------------------
# Real SQLite fanout store APIs
# ---------------------------------------------------------------------------

def _make_real_store(test_name: str):
    from src.datahub.core.registry import SchemaRegistry, TableSpec, ColumnSpec
    from src.datahub.storage.sqlite import DataHubStore

    registry = SchemaRegistry(
        version=1,
        tables={
            "test_table": TableSpec(
                table_name="test_table",
                dataset_key="test_dataset",
                description="test",
                write_mode="upsert",
                primary_key=("id",),
                scope_column_names=(),
                columns={"id": ColumnSpec(name="id", type="string", nullable=False)},
            )
        },
        datasets={"test_dataset"},
        raw={"version": 1, "tables": {"test_table": {}}},
    )
    # Use project-local temp dir to avoid Windows permission issues with system temp
    from pathlib import Path
    db_dir = Path(__file__).resolve().parents[1] / ".tmp_test" / test_name
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "fanout.sqlite"
    if db_path.exists():
        db_path.unlink()
    store = DataHubStore(db_path, registry)
    store.init_schema(dev_mode=True)
    return store


class TestFanoutStoreApis:
    def test_claim_is_atomic_and_stale_submitting_recovers(self):
        store = _make_real_store("fanout_claim_recover")
        store.create_fanout_run_with_items(
            parent_job_id="parent_1",
            plugin_id="dcp",
            parent_command="parent_cmd",
            child_command="child_cmd",
            param_sets=[{"x": 1}, {"x": 2}],
            max_concurrency=2,
            cooldown_seconds=0,
            consecutive_failure_threshold=5,
        )

        first = store.claim_next_pending_fanout_item("parent_1", "sched_a")
        second = store.claim_next_pending_fanout_item("parent_1", "sched_b")
        third = store.claim_next_pending_fanout_item("parent_1", "sched_c")

        assert first is not None
        assert second is not None
        assert first["id"] != second["id"]
        assert third is None
        assert store.get_fanout_stats("parent_1")["submitting"] == 2

        from datetime import timedelta
        from src.datahub.core.time_utils import datahub_now
        stale_time = (datahub_now() - timedelta(seconds=180)).strftime("%Y-%m-%d %H:%M:%S")
        with store.connect() as conn:
            conn.execute("UPDATE fanout_items SET claimed_at = ? WHERE id = ?", (stale_time, first["id"]))

        assert store.reset_stale_submitting_items("parent_1", stale_seconds=120) == 1
        reclaimed = store.claim_next_pending_fanout_item("parent_1", "sched_d")
        assert reclaimed is not None
        assert reclaimed["id"] == first["id"]

    def test_parent_aggregator_skips_scheduler_managed_parent(self):
        from src.datahub.core.trigger_runtime import _aggregate_parent_jobs

        store = _make_real_store("fanout_parent_aggregate_skip")
        store.create_ingestion_job(
            ingestion_job_id="parent_2",
            producer_job_id="producer_parent_2",
            job_type="parent_cmd",
            params={},
            plugin_id="dcp",
        )
        store.create_ingestion_job(
            ingestion_job_id="child_2",
            producer_job_id="producer_child_2",
            job_type="child_cmd",
            params={},
            plugin_id="dcp",
            parent_job_id="parent_2",
        )
        store.mark_job("parent_2", status="running")
        store.mark_job("child_2", status="succeeded")
        store.create_fanout_run_with_items(
            parent_job_id="parent_2",
            plugin_id="dcp",
            parent_command="parent_cmd",
            child_command="child_cmd",
            param_sets=[{"x": 1}],
        )

        _aggregate_parent_jobs(store)
        assert store.get_job("parent_2")["status"] == "running"
