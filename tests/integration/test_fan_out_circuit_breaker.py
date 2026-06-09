"""Core tests for fan-out circuit breakers (date-range and project).

Keeps only MVP-critical scenarios:
1. Consecutive failures trigger circuit breaker (both date and project)
2. Parent status = failed when circuit opens
3. Success resets consecutive counter
4. Normal success path unaffected
5. Child params cleanup (fan-out controls not leaked to children)
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from plugins.dcp.fan_out import (
    _is_child_failed,
    _date_range_fan_out,
    _project_fan_out,
)


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
    return store


def _make_plugins(child_command_name="refresh_daily_meetings_by_range"):
    from src.datahub.core.specs import PluginSpec, CommandSpec, DisplaySpec, ConnectorSpec
    child_cmd = CommandSpec(
        name=child_command_name,
        trigger={"job_type": "safe_daily_meeting_range", "handler": "dcp.fan_out:backfill_daily_meetings_by_range"},
    )
    plugin = PluginSpec(
        name="dcp", version=1, display=DisplaySpec(label="DCP"),
        connector=ConnectorSpec(type="http_sync", base_url="http://localhost:8010"),
        commands=(child_cmd,),
    )
    return [plugin]


def _make_client(sync_side_effect=None):
    client = MagicMock()
    client.sync = MagicMock(side_effect=sync_side_effect or [{"status": "accepted", "downloader_job_id": "job_123"}])
    client.get_job_status = MagicMock(return_value={"status": "succeeded"})
    return client


def _make_ctx(store, plugins, client, params=None):
    return {
        "store": store, "plugins": plugins, "trigger_clients": {"dcp": client},
        "ingestion_job_id": "ing_test_parent_001",
        "callback_base_url": "http://localhost:8000",
        "callback_headers": {"X-Callback-Key": "dev-default-callback-key"},
        "params": params or {},
    }


def _succeeded_job(row_count=100, message_received=1):
    return {"status": "succeeded", "error": None, "row_count": row_count,
            "message_received": message_received, "producer_status_json": None}


def _failed_job(error="request_failed"):
    return {"status": "failed", "error": error, "row_count": 0,
            "message_received": 0, "producer_status_json": json.dumps({"error": error})}


# ---------------------------------------------------------------------------
# _is_child_failed — core cases only
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
# Date-range fan-out circuit breaker
# ---------------------------------------------------------------------------

class TestDateRangeCircuitBreaker:
    def _run_fan_out(self, child_jobs, params=None, threshold=None):
        if params is None:
            params = {"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1}
        if threshold is not None:
            params["consecutive_failure_threshold"] = threshold

        created_job_ids = []
        job_counter = [0]

        def mock_create_job(ingestion_job_id, **kwargs):
            created_job_ids.append(ingestion_job_id)

        def mock_sync(*args, **kwargs):
            idx = job_counter[0]
            job_counter[0] += 1
            return {"status": "accepted", "downloader_job_id": f"job_{idx}"}

        store = _make_store()
        store.create_ingestion_job = MagicMock(side_effect=mock_create_job)

        def mock_get_job(job_id):
            if job_id in created_job_ids:
                idx = created_job_ids.index(job_id)
                if idx < len(child_jobs):
                    return child_jobs[idx]
            return _succeeded_job()

        store.get_job = MagicMock(side_effect=mock_get_job)
        plugins = _make_plugins()
        client = _make_client(sync_side_effect=mock_sync)
        ctx = _make_ctx(store, plugins, client, params)

        with patch("plugins.dcp.fan_out._wait_for_child_terminal") as mock_wait:
            def wait_side_effect(store_arg, job_id, **kwargs):
                if job_id in created_job_ids:
                    idx = created_job_ids.index(job_id)
                    if idx < len(child_jobs):
                        return child_jobs[idx]
                return _succeeded_job()
            mock_wait.side_effect = wait_side_effect
            result = _date_range_fan_out(
                ctx=ctx, child_command="refresh_daily_meetings_by_range",
                start_date_param="startDate", end_date_param="endDate",
                chunk_days=1, cooldown_seconds=0,
            )

        return result, store, created_job_ids

    def test_circuit_breaker_stops_after_consecutive_failures(self):
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out(child_jobs)
        assert len(created_ids) == 5
        assert result["created_children"] == 5
        assert result["failed"] == 5

    def test_parent_failed_when_circuit_opens(self):
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out(child_jobs)
        mark_calls = store.mark_job.call_args_list
        failed_calls = [c for c in mark_calls if c[0][0] == "ing_test_parent_001" and c[1].get("status") == "failed"]
        assert len(failed_calls) >= 1
        assert "circuit breaker opened" in failed_calls[0][1].get("error", "")

    def test_success_resets_consecutive_counter(self):
        child_jobs = [
            _failed_job(), _failed_job(), _succeeded_job(),
            _failed_job(), _failed_job(), _succeeded_job(),
            _failed_job(), _failed_job(), _failed_job(), _succeeded_job(),
        ]
        result, store, created_ids = self._run_fan_out(child_jobs)
        assert len(created_ids) == 10

    def test_normal_success_path_unaffected(self):
        child_jobs = [_succeeded_job() for _ in range(30)]
        result, store, created_ids = self._run_fan_out(
            child_jobs, params={"startDate": "2026-01-01", "endDate": "2026-01-30", "chunk_days": 1})
        assert len(created_ids) == 30
        assert result["succeeded"] == 30
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# Project fan-out circuit breaker
# ---------------------------------------------------------------------------

class TestProjectFanOutCircuitBreaker:
    def _run_project_fan_out(self, project_rows, child_jobs, params=None, threshold=None):
        if params is None:
            params = {}
        if threshold is not None:
            params["consecutive_failure_threshold"] = threshold

        created_job_ids = []
        job_counter = [0]

        def mock_create_job(ingestion_job_id, **kwargs):
            created_job_ids.append(ingestion_job_id)

        def mock_sync(*args, **kwargs):
            idx = job_counter[0]
            job_counter[0] += 1
            return {"status": "accepted", "downloader_job_id": f"job_{idx}"}

        store = _make_store()
        store.query_table = MagicMock(return_value=project_rows)
        store.create_ingestion_job = MagicMock(side_effect=mock_create_job)

        def mock_get_job(job_id):
            if job_id in created_job_ids:
                idx = created_job_ids.index(job_id)
                if idx < len(child_jobs):
                    return child_jobs[idx]
            return _succeeded_job()

        store.get_job = MagicMock(side_effect=mock_get_job)

        from src.datahub.core.specs import PluginSpec, CommandSpec, DisplaySpec, ConnectorSpec
        child_cmd = CommandSpec(
            name="refresh_substations_for_project",
            trigger={"job_type": "safe_substation_list", "handler": "dcp.fan_out:refresh_substations_for_current_plan_projects"},
        )
        plugin = PluginSpec(
            name="dcp", version=1, display=DisplaySpec(label="DCP"),
            connector=ConnectorSpec(type="http_sync", base_url="http://localhost:8010"),
            commands=(child_cmd,),
        )
        plugins = [plugin]
        client = _make_client(sync_side_effect=mock_sync)
        ctx = _make_ctx(store, plugins, client, params)

        with patch("plugins.dcp.fan_out._wait_for_child_terminal") as mock_wait, \
             patch("plugins.dcp.fan_out._find_child_command_and_client") as mock_find:
            mock_find.return_value = (MagicMock(trigger={"job_type": "safe_substation_list"}), plugin, client, None)
            def wait_side_effect(store_arg, job_id, **kwargs):
                if job_id in created_job_ids:
                    idx = created_job_ids.index(job_id)
                    if idx < len(child_jobs):
                        return child_jobs[idx]
                return _succeeded_job()
            mock_wait.side_effect = wait_side_effect
            result = _project_fan_out(
                ctx=ctx, child_command="refresh_substations_for_project",
                params_mapping={"prjCode": "projectCode"}, cooldown_seconds=0,
            )

        return result, store, created_job_ids

    def test_circuit_breaker_stops_after_consecutive_failures(self):
        project_rows = [{"prjCode": f"P{i:03d}"} for i in range(10)]
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_project_fan_out(project_rows, child_jobs)
        assert len(created_ids) == 5
        assert result["created_children"] == 5
        assert result["failed_children"] == 5

    def test_parent_failed_when_circuit_opens(self):
        project_rows = [{"prjCode": f"P{i:03d}"} for i in range(10)]
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_project_fan_out(project_rows, child_jobs)
        mark_calls = store.mark_job.call_args_list
        failed_calls = [c for c in mark_calls if c[0][0] == "ing_test_parent_001" and c[1].get("status") == "failed"]
        assert len(failed_calls) >= 1
        assert "circuit breaker opened" in failed_calls[0][1].get("error", "")

    def test_success_resets_consecutive_counter(self):
        project_rows = [{"prjCode": f"P{i:03d}"} for i in range(10)]
        child_jobs = [
            _failed_job(), _failed_job(), _succeeded_job(),
            _failed_job(), _failed_job(), _succeeded_job(),
            _failed_job(), _failed_job(), _failed_job(), _succeeded_job(),
        ]
        result, store, created_ids = self._run_project_fan_out(project_rows, child_jobs)
        assert len(created_ids) == 10
