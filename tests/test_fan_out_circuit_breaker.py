"""Tests for date-range fan-out circuit breaker.

Covers:
1. 5 consecutive child failures → fan-out stops, no 6th child created
2. Parent status = failed when circuit opens
3. Parent error contains "circuit breaker opened"
4. result_json contains skipped_remaining_dates
5. Success between failures resets consecutive counter
6. Normal 30-day success path unaffected
7. Project fan-out unaffected
"""

from __future__ import annotations

import json
import time
from datetime import date, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from plugins.dcp.fan_out import (
    _DEFAULT_CONSECUTIVE_FAILURE_THRESHOLD,
    _is_child_failed,
    _wait_for_child_terminal,
    _date_range_fan_out,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_store(jobs: dict[str, dict] | None = None):
    """Create a mock store with pre-populated job data."""
    store = MagicMock()
    _jobs = dict(jobs or {})

    def _get_job(job_id):
        return _jobs.get(job_id)

    store.get_job = MagicMock(side_effect=_get_job)
    store.mark_job = MagicMock()
    store.query_table = MagicMock(return_value=[])
    store.connect = MagicMock()
    return store


def _make_child_command():
    """Create a mock child command spec."""
    cmd = MagicMock()
    cmd.trigger = {"job_type": "safe_daily_meeting_range"}
    return cmd


def _make_plugins(child_command_name="refresh_daily_meetings_by_range"):
    """Create mock plugins list with a child command."""
    from src.datahub.core.specs import PluginSpec, CommandSpec, DisplaySpec, ConnectorSpec

    child_cmd = CommandSpec(
        name=child_command_name,
        trigger={"job_type": "safe_daily_meeting_range", "handler": "dcp.fan_out:backfill_daily_meetings_by_range"},
    )
    plugin = PluginSpec(
        name="dcp",
        version=1,
        display=DisplaySpec(label="DCP"),
        connector=ConnectorSpec(type="http_sync", base_url="http://localhost:8010"),
        commands=(child_cmd,),
    )
    return [plugin]


def _make_client(sync_side_effect=None):
    """Create a mock trigger client."""
    client = MagicMock()
    client.sync = MagicMock(side_effect=sync_side_effect or [
        {"status": "accepted", "downloader_job_id": "job_123"}
    ])
    client.get_job_status = MagicMock(return_value={"status": "succeeded"})
    return client


def _make_ctx(store, plugins, client, params=None):
    """Create a standard fan-out context dict."""
    return {
        "store": store,
        "plugins": plugins,
        "trigger_clients": {"dcp": client},
        "ingestion_job_id": "ing_test_parent_001",
        "callback_base_url": "http://localhost:8000",
        "callback_headers": {"X-Callback-Key": "dev-default-callback-key"},
        "params": params or {},
    }


def _succeeded_job(row_count=100, message_received=1):
    """Create a succeeded job dict."""
    return {
        "status": "succeeded",
        "error": None,
        "row_count": row_count,
        "message_received": message_received,
        "producer_status_json": None,
    }


def _failed_job(error="request_failed"):
    """Create a failed job dict."""
    return {
        "status": "failed",
        "error": error,
        "row_count": 0,
        "message_received": 0,
        "producer_status_json": json.dumps({"error": error}),
    }


def _partial_empty_job():
    """Create a partial job with no data (effectively a failure)."""
    return {
        "status": "partial",
        "error": None,
        "row_count": 0,
        "message_received": 0,
        "producer_status_json": None,
    }


def _request_failed_job():
    """Create a job with request_failed in producer_status."""
    return {
        "status": "partial",
        "error": None,
        "row_count": 0,
        "message_received": 0,
        "producer_status_json": json.dumps({
            "collects": [{"error": {"error_type": "request_failed"}}]
        }),
    }


# ---------------------------------------------------------------------------
# Tests for _is_child_failed
# ---------------------------------------------------------------------------

class TestIsChildFailed:
    def test_none_job_is_failed(self):
        assert _is_child_failed(None) is True

    def test_succeeded_job_not_failed(self):
        assert _is_child_failed(_succeeded_job()) is False

    def test_failed_status_is_failed(self):
        assert _is_child_failed(_failed_job()) is True

    def test_cancelled_status_is_failed(self):
        assert _is_child_failed({"status": "cancelled", "error": None, "row_count": 0, "message_received": 0, "producer_status_json": None}) is True

    def test_error_non_empty_is_failed(self):
        assert _is_child_failed({"status": "succeeded", "error": "something wrong", "row_count": 100, "message_received": 1, "producer_status_json": None}) is True

    def test_request_failed_in_producer_status(self):
        assert _is_child_failed(_request_failed_job()) is True

    def test_partial_empty_is_failed(self):
        assert _is_child_failed(_partial_empty_job()) is True

    def test_partial_with_data_not_failed(self):
        job = {"status": "partial", "error": None, "row_count": 50, "message_received": 1, "producer_status_json": None}
        assert _is_child_failed(job) is False


# ---------------------------------------------------------------------------
# Tests for circuit breaker in _date_range_fan_out
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    """Test the consecutive failure circuit breaker in date-range fan-out."""

    def _run_fan_out_with_jobs(self, child_jobs, params=None, threshold=None):
        """Run _date_range_fan_out with mocked child job results.

        child_jobs: list of job dicts that get_job returns for each child.
        """
        if params is None:
            params = {"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1}
        if threshold is not None:
            params["consecutive_failure_threshold"] = threshold

        # Track created child job IDs
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

        # Set up get_job to return appropriate results for each child
        def mock_get_job(job_id):
            if job_id in created_job_ids:
                idx = created_job_ids.index(job_id)
                if idx < len(child_jobs):
                    return child_jobs[idx]
                return _succeeded_job()
            return None

        store.get_job = MagicMock(side_effect=mock_get_job)

        plugins = _make_plugins()
        client = _make_client(sync_side_effect=mock_sync)
        ctx = _make_ctx(store, plugins, client, params)

        # Patch _wait_for_child_terminal to return immediately
        with patch("plugins.dcp.fan_out._wait_for_child_terminal") as mock_wait:
            def wait_side_effect(store_arg, job_id, **kwargs):
                if job_id in created_job_ids:
                    idx = created_job_ids.index(job_id)
                    if idx < len(child_jobs):
                        return child_jobs[idx]
                return _succeeded_job()

            mock_wait.side_effect = wait_side_effect

            result = _date_range_fan_out(
                ctx=ctx,
                child_command="refresh_daily_meetings_by_range",
                start_date_param="startDate",
                end_date_param="endDate",
                chunk_days=1,
                cooldown_seconds=0,  # No cooldown in tests
            )

        return result, store, created_job_ids

    def test_circuit_breaker_stops_after_5_consecutive_failures(self):
        """5 consecutive failures → fan-out stops, no 6th child created."""
        # 10 days, all fail
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1},
        )

        # Should only create 5 children (threshold), not 10
        assert len(created_ids) == 5
        assert result["created_children"] == 5
        assert result["failed"] == 5
        assert result["succeeded"] == 0

    def test_parent_failed_when_circuit_opens(self):
        """Parent status should be 'failed' when circuit breaker opens."""
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1},
        )

        # Check mark_job was called with status="failed"
        mark_calls = store.mark_job.call_args_list
        parent_failed_call = None
        for call in mark_calls:
            if call[0][0] == "ing_test_parent_001" and call[1].get("status") == "failed":
                parent_failed_call = call
                break

        assert parent_failed_call is not None

    def test_parent_error_contains_circuit_breaker_opened(self):
        """Parent error should contain 'circuit breaker opened'."""
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1},
        )

        mark_calls = store.mark_job.call_args_list
        error_msg = None
        for call in mark_calls:
            if call[0][0] == "ing_test_parent_001" and call[1].get("status") == "failed":
                error_msg = call[1].get("error")
                break

        assert error_msg is not None
        assert "circuit breaker opened" in error_msg

    def test_result_contains_skipped_remaining_dates(self):
        """result_json should contain skipped_remaining_dates."""
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1},
        )

        assert "skipped_remaining_dates" in result
        assert result["skipped_remaining_dates"] == 5  # 10 total - 5 created
        assert "first_failed_date" in result
        assert "last_failed_date" in result
        assert "consecutive_failure_threshold" in result

    def test_success_resets_consecutive_counter(self):
        """A success between failures resets the consecutive failure counter."""
        # Pattern: fail, fail, succeed, fail, fail, succeed, fail, fail, fail, succeed
        child_jobs = [
            _failed_job(), _failed_job(),  # 2 consecutive
            _succeeded_job(),               # reset
            _failed_job(), _failed_job(),   # 2 consecutive
            _succeeded_job(),               # reset
            _failed_job(), _failed_job(), _failed_job(),  # 3 consecutive
            _succeeded_job(),
        ]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={"startDate": "2026-01-01", "endDate": "2026-01-10", "chunk_days": 1},
        )

        # All 10 children should be created (never reached 5 consecutive)
        assert len(created_ids) == 10
        assert result["created_children"] == 10
        assert result["failed"] == 7
        assert result["succeeded"] == 3

    def test_normal_success_path_unaffected(self):
        """30-day normal success path should work without circuit breaker interference."""
        # 30 days, all succeed
        child_jobs = [_succeeded_job() for _ in range(30)]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={"startDate": "2026-01-01", "endDate": "2026-01-30", "chunk_days": 1},
        )

        assert len(created_ids) == 30
        assert result["created_children"] == 30
        assert result["succeeded"] == 30
        assert result["failed"] == 0
        assert "skipped_remaining_dates" not in result

    def test_custom_threshold_override(self):
        """consecutive_failure_threshold=3 should stop after 3 failures."""
        child_jobs = [_failed_job() for _ in range(10)]
        result, store, created_ids = self._run_fan_out_with_jobs(
            child_jobs,
            params={
                "startDate": "2026-01-01", "endDate": "2026-01-10",
                "chunk_days": 1, "consecutive_failure_threshold": 3,
            },
        )

        assert len(created_ids) == 3
        assert result["created_children"] == 3
        assert result["skipped_remaining_dates"] == 7


class TestProjectFanOutUnaffected:
    """Verify project fan-out is not affected by circuit breaker changes."""

    def test_project_fan_out_still_works(self):
        """Project fan-out should work as before without circuit breaker."""
        from plugins.dcp.fan_out import _project_fan_out

        store = _make_store()
        # Return some project rows for dcp_plan_projects query
        store.query_table = MagicMock(return_value=[
            {"prjCode": "P001"},
            {"prjCode": "P002"},
        ])

        plugins = _make_plugins("refresh_towers_for_project")
        client = _make_client()
        ctx = _make_ctx(store, plugins, client)

        # Patch _run_child_job and _find_child_command_and_client
        with patch("plugins.dcp.fan_out._run_child_job") as mock_run, \
             patch("plugins.dcp.fan_out._find_child_command_and_client") as mock_find:
            mock_find.return_value = (MagicMock(trigger={"job_type": "safe_tower_list"}), plugins[0], client, None)
            mock_run.return_value = ("ing_child_001", "accepted", None)
            result = _project_fan_out(
                ctx=ctx,
                child_command="refresh_towers_for_project",
                params_mapping={"prjCode": "projectCode"},
                cooldown_seconds=0,
            )

        assert result["total"] == 2
        assert result["succeeded"] == 2
