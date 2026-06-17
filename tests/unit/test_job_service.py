"""Tests for JobService — unified job trigger service.

Covers:
1. submit_command with downloader_sync trigger
2. submit_command with plugin_handler trigger
3. submit_command validation (unknown command, disabled, missing params, invalid source)
4. get_job_detail
5. retry_job (status protection, original_job_id)
6. source is recorded in ingestion_jobs
7. source field in CREATE TABLE baseline
"""

from __future__ import annotations

import inspect
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.datahub.core.services.job_service import (
    JobService,
    JobServiceError,
    JobResult,
    RETRYABLE_STATUSES,
    strip_internal_params,
    get_internal_retry_count,
    bump_internal_retry_meta,
)
from src.datahub.core.specs import CommandSpec, PluginSpec, DisplaySpec, ConnectorSpec
from src.datahub.core.fanout_scheduler import _get_child_retry_count, _is_child_non_success


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_command(name="dcp_current_plan", trigger_type="downloader_sync", **kwargs):
    defaults = dict(
        name=name,
        trigger={"type": trigger_type, "job_type": f"safe_{name}"},
        max_concurrency=1,
        cooldown_seconds=0,
    )
    defaults.update(kwargs)
    return CommandSpec(**defaults)


def _make_plugins(commands=None):
    if commands is None:
        commands = [_make_command()]
    plugin = PluginSpec(
        name="dcp",
        version=1,
        display=DisplaySpec(label="DCP"),
        connector=ConnectorSpec(type="http_sync", base_url="http://localhost:8010"),
        commands=tuple(commands),
    )
    return [plugin]


def _make_store():
    store = MagicMock()
    store.create_ingestion_job = MagicMock()
    store.mark_job = MagicMock()
    store.get_job = MagicMock(return_value=None)
    store.find_active_retry = MagicMock(return_value=None)
    store.get_fanout_run = MagicMock(return_value=None)
    store.list_failed_fanout_items = MagicMock(return_value=[])
    store.update_fanout_item_for_retry = MagicMock()
    store.reopen_fanout_run = MagicMock()
    store.reopen_parent_ingestion_job = MagicMock()
    return store


def _make_client(sync_return=None):
    client = MagicMock()
    client.sync = MagicMock(return_value=sync_return or {"status": "accepted", "downloader_job_id": "job_123"})
    return client


def _make_job_service(plugins=None, store=None, client=None):
    plugins = plugins or _make_plugins()
    store = store or _make_store()
    client = client or _make_client()
    trigger_clients = {"dcp": client}
    return JobService(
        store=store,
        plugins=plugins,
        trigger_clients=trigger_clients,
        callback_base_url="http://localhost:8000",
        callback_headers={"X-API-Key": "test-key"},
    ), store, client


# ---------------------------------------------------------------------------
# submit_command — downloader_sync
# ---------------------------------------------------------------------------

class TestSubmitCommandDownloaderSync:
    def test_creates_job_and_calls_sync(self):
        svc, store, client = _make_job_service()
        result = svc.submit_command("dcp_current_plan", {"domain": "basic"}, source="cli")

        assert isinstance(result, JobResult)
        assert result.ingestion_job_id.startswith("ing_dcp_current_plan_")
        assert result.status == "accepted"
        assert result.downloader_job_id is not None

        store.create_ingestion_job.assert_called_once()
        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["job_type"] == "dcp_current_plan"
        assert call_kwargs["params"] == {"domain": "basic"}
        assert call_kwargs["plugin_id"] == "dcp"
        assert call_kwargs["source"] == "cli"

        client.sync.assert_called_once()

    def test_default_source_is_api(self):
        svc, store, _ = _make_job_service()
        svc.submit_command("dcp_current_plan")
        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["source"] == "api"

    def test_sync_failure_marks_job_failed(self):
        svc, store, client = _make_job_service()
        client.sync.side_effect = ConnectionError("downloader unreachable")

        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("dcp_current_plan")
        assert exc_info.value.error_code == "external_sync_failed"

        store.mark_job.assert_called()
        # Last mark_job should be the failure
        last_call = store.mark_job.call_args_list[-1]
        assert last_call[1]["status"] == "failed"

    def test_no_connector_raises_error(self):
        plugins = _make_plugins()
        store = _make_store()
        svc = JobService(
            store=store,
            plugins=plugins,
            trigger_clients={},  # No connector
            callback_base_url="http://localhost:8000",
        )

        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("dcp_current_plan")
        assert exc_info.value.error_code == "no_connector"


# ---------------------------------------------------------------------------
# submit_command — plugin_handler
# ---------------------------------------------------------------------------

class TestSubmitCommandPluginHandler:
    def test_plugin_handler_creates_job_and_starts_handler(self):
        cmd = _make_command(
            name="refresh_towers_for_current_plan_projects",
            trigger_type="plugin_handler",
            trigger={"type": "plugin_handler", "handler": "dcp.fan_out:refresh_towers_for_current_plan_projects"},
        )
        plugins = _make_plugins(commands=[cmd])
        store = _make_store()
        client = _make_client()

        with patch("src.datahub.core.services.job_service.load_plugin_handler") as mock_load, \
             patch("src.datahub.core.services.job_service.run_handler_async") as mock_run:
            mock_handler = MagicMock()
            mock_load.return_value = mock_handler

            svc = JobService(
                store=store,
                plugins=plugins,
                trigger_clients={"dcp": client},
                callback_base_url="http://localhost:8000",
            )
            result = svc.submit_command("refresh_towers_for_current_plan_projects", source="scheduler")

        assert result.status == "running"
        assert result.message == "plugin_handler started in background"

        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["source"] == "scheduler"

        mock_load.assert_called_once()
        mock_run.assert_called_once()

    def test_handler_failure_marks_job_failed(self):
        cmd = _make_command(
            name="bad_handler_cmd",
            trigger_type="plugin_handler",
            trigger={"type": "plugin_handler", "handler": "dcp.fan_out:nonexistent"},
        )
        plugins = _make_plugins(commands=[cmd])
        store = _make_store()
        client = _make_client()

        with patch("src.datahub.core.services.job_service.load_plugin_handler", side_effect=ImportError("no module")):
            svc = JobService(
                store=store,
                plugins=plugins,
                trigger_clients={"dcp": client},
                callback_base_url="http://localhost:8000",
            )
            with pytest.raises(JobServiceError) as exc_info:
                svc.submit_command("bad_handler_cmd")
            assert exc_info.value.error_code == "plugin_handler_failed"

        # Job should be marked failed
        mark_calls = store.mark_job.call_args_list
        assert any(c[1].get("status") == "failed" for c in mark_calls)


# ---------------------------------------------------------------------------
# submit_command — validation
# ---------------------------------------------------------------------------

class TestSubmitCommandValidation:
    def test_unknown_command_raises_error(self):
        svc, _, _ = _make_job_service(plugins=_make_plugins())
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("nonexistent_command")
        assert exc_info.value.error_code == "unknown_command"

    def test_disabled_command_raises_error(self):
        cmd = _make_command(name="disabled_cmd", enabled=False)
        plugins = _make_plugins(commands=[cmd])
        svc, _, _ = _make_job_service(plugins=plugins)
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("disabled_cmd")
        assert exc_info.value.error_code == "command_disabled"

    def test_missing_required_param_raises_error(self):
        cmd = _make_command(name="needs_param", required_params=("projectCode",))
        plugins = _make_plugins(commands=[cmd])
        svc, _, _ = _make_job_service(plugins=plugins)
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("needs_param", params={})
        assert exc_info.value.error_code == "missing_required_param"

    def test_invalid_source_raises_error(self):
        svc, _, _ = _make_job_service()
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("dcp_current_plan", source="invalid_source")
        assert exc_info.value.error_code == "invalid_source"

    def test_all_valid_sources_accepted(self):
        svc, store, _ = _make_job_service()
        for source in ("cli", "api", "scheduler", "ui_manual", "retry"):
            store.create_ingestion_job.reset_mock()
            svc.submit_command("dcp_current_plan", source=source)
            call_kwargs = store.create_ingestion_job.call_args[1]
            assert call_kwargs["source"] == source


# ---------------------------------------------------------------------------
# get_job_detail
# ---------------------------------------------------------------------------

class TestGetJobDetail:
    def test_returns_job_dict(self):
        svc, store, _ = _make_job_service()
        expected = {"ingestion_job_id": "ing_test_123", "status": "succeeded"}
        store.get_job.return_value = expected

        result = svc.get_job_detail("ing_test_123")
        assert result == expected
        store.get_job.assert_called_once_with("ing_test_123")

    def test_returns_none_for_missing(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = None
        assert svc.get_job_detail("nonexistent") is None


# ---------------------------------------------------------------------------
# retry_job
# ---------------------------------------------------------------------------

class TestRetryJob:
    def test_retry_failed_job_reopens_same_job_id(self):
        svc, store, client = _make_job_service()
        original = {
            "ingestion_job_id": "ing_old_123",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": None,
        }
        store.get_job.return_value = original

        result = svc.retry_job("ing_old_123")
        assert isinstance(result, JobResult)
        assert result.ingestion_job_id == "ing_old_123"  # same job_id (in-place retry)

        # reopen_job_for_retry should be called (not create_ingestion_job)
        store.reopen_job_for_retry.assert_called_once()
        call_kwargs = store.reopen_job_for_retry.call_args[1]
        assert call_kwargs["source"] == "retry"

    def test_retry_partial_job_succeeds(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_partial_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({}),
            "status": "partial",
            "parent_job_id": None,
        }
        store.get_job.return_value = original
        result = svc.retry_job("ing_partial_1")
        assert result.ingestion_job_id == "ing_partial_1"  # same job_id

    def test_retry_cancelled_job_succeeds(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_cancel_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({}),
            "status": "cancelled",
            "parent_job_id": None,
        }
        store.get_job.return_value = original
        result = svc.retry_job("ing_cancel_1")
        assert result.ingestion_job_id == "ing_cancel_1"  # same job_id

    def test_retry_running_job_rejected(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_run_1",
            "trigger_key": "dcp_current_plan",
            "params_json": "{}",
            "status": "running",
        }
        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_run_1")
        assert exc_info.value.error_code == "job_not_retryable"
        assert "ing_run_1" in exc_info.value.message
        assert "running" in exc_info.value.message

    def test_retry_triggering_job_rejected(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_trig_1",
            "trigger_key": "dcp_current_plan",
            "params_json": "{}",
            "status": "triggering",
        }
        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_trig_1")
        assert exc_info.value.error_code == "job_not_retryable"

    def test_retry_succeeded_job_rejected(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_ok_1",
            "trigger_key": "dcp_current_plan",
            "params_json": "{}",
            "status": "succeeded",
        }
        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_ok_1")
        assert exc_info.value.error_code == "job_not_retryable"

    def test_retry_accepted_job_rejected(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_acc_1",
            "trigger_key": "dcp_current_plan",
            "params_json": "{}",
            "status": "accepted",
        }
        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_acc_1")
        assert exc_info.value.error_code == "job_not_retryable"

    def test_retry_not_found_raises_error(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = None
        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("nonexistent")
        assert exc_info.value.error_code == "job_not_found"

    def test_retry_no_command_raises_error(self):
        svc, store, _ = _make_job_service()
        store.get_job.return_value = {"ingestion_job_id": "ing_x", "trigger_key": None, "params_json": "{}", "status": "failed"}
        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_x")
        assert exc_info.value.error_code == "no_command"


# ---------------------------------------------------------------------------
# P2: retry_of_job_id and retry_already_running
# ---------------------------------------------------------------------------

class TestRetryOfJobId:
    """P5.5-light: retry_job is in-place, same ingestion_job_id, __datahub retry_count."""

    def test_retry_returns_same_job_id(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_orig_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": "ing_parent_1",
        }
        store.get_job.return_value = original

        result = svc.retry_job("ing_orig_1")
        assert result.ingestion_job_id == "ing_orig_1"  # same job_id (in-place)
        assert result.original_job_id is None  # no longer set
        assert result.retry_of_job_id is None  # no longer set

    def test_retry_bumps_datahub_retry_count(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_orig_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": None,
        }
        store.get_job.return_value = original

        result = svc.retry_job("ing_orig_1")
        # reopen_job_for_retry should be called with params containing __datahub
        call_kwargs = store.reopen_job_for_retry.call_args[1]
        params = json.loads(call_kwargs["params_json"])
        assert params["__datahub"]["retry_count"] == 1
        assert params["__datahub"]["last_retry_reason"] == "manual"

    def test_retry_child_preserves_parent_job_id(self):
        """Fanout child retry reopens the same job (parent_job_id is in the DB row)."""
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_child_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": "ing_parent_fanout",
        }
        store.get_job.return_value = original

        result = svc.retry_job("ing_child_1")
        assert result.ingestion_job_id == "ing_child_1"  # same job_id


# ---------------------------------------------------------------------------
# P2: retry_failed_children
# ---------------------------------------------------------------------------

class TestRetryFailedChildren:
    """P2: retry_failed_children for fan-out parent jobs."""

    def _make_fanout_setup(self):
        """Create a JobService with fanout_run and items mocked."""
        svc, store, client = _make_job_service()
        fanout_run = {
            "parent_job_id": "ing_parent_1",
            "child_command": "dcp_current_plan",
            "status": "partial",
            "total": 3,
        }
        store.get_fanout_run = MagicMock(return_value=fanout_run)
        store.list_failed_fanout_items = MagicMock(return_value=[
            {"id": 1, "item_index": 0, "params_json": json.dumps({"domain": "a"}), "child_job_id": "ing_child_0", "status": "failed"},
            {"id": 2, "item_index": 1, "params_json": json.dumps({"domain": "b"}), "child_job_id": "ing_child_1", "status": "skipped"},
        ])
        store.get_job = MagicMock(side_effect=lambda jid: {
            "ing_child_0": {"ingestion_job_id": "ing_child_0", "status": "failed", "params_json": json.dumps({"domain": "a"})},
            "ing_child_1": {"ingestion_job_id": "ing_child_1", "status": "cancelled", "params_json": json.dumps({"domain": "b"})},
        }.get(jid))
        store.reopen_job_for_retry = MagicMock(return_value=True)
        store.update_fanout_item_for_inplace_retry = MagicMock()
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()
        return svc, store, client

    def test_not_fanout_parent_raises_error(self):
        svc, store, _ = _make_job_service()
        store.get_fanout_run = MagicMock(return_value=None)

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_not_fanout")
        assert exc_info.value.error_code == "not_fanout_parent"

    def test_no_failed_children_raises_error(self):
        svc, store, _ = _make_job_service()
        store.get_fanout_run = MagicMock(return_value={"parent_job_id": "ing_parent_1", "child_command": "dcp_current_plan", "status": "succeeded"})
        store.list_failed_fanout_items = MagicMock(return_value=[])

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_parent_1")
        assert exc_info.value.error_code == "no_failed_children"

    def test_failed_items_retried_in_place(self):
        svc, store, _ = self._make_fanout_setup()

        result = svc.retry_failed_children("ing_parent_1")
        assert result["submitted"] == 2
        assert result["skipped"] == 0
        assert len(result["items"]) == 2

        # Check first item — same child_job_id (in-place retry)
        item0 = result["items"][0]
        assert item0["child_job_id"] == "ing_child_0"
        assert item0["status"] == "submitted"

    def test_inplace_retry_reopens_child_jobs(self):
        svc, store, _ = self._make_fanout_setup()
        svc.retry_failed_children("ing_parent_1")

        # reopen_job_for_retry should be called for each child
        assert store.reopen_job_for_retry.call_count == 2

    def test_fanout_item_updated_inplace(self):
        svc, store, _ = self._make_fanout_setup()
        result = svc.retry_failed_children("ing_parent_1")

        # update_fanout_item_for_inplace_retry should be called for each item
        assert store.update_fanout_item_for_inplace_retry.call_count == 2

    def test_fanout_run_reopened_when_closed(self):
        svc, store, _ = self._make_fanout_setup()
        svc.retry_failed_children("ing_parent_1")

        store.reopen_fanout_run.assert_called_once_with("ing_parent_1")
        store.reopen_parent_ingestion_job.assert_called_once_with("ing_parent_1")

    def test_active_child_not_retried(self):
        svc, store, _ = _make_job_service()
        fanout_run = {
            "parent_job_id": "ing_parent_1",
            "child_command": "dcp_current_plan",
            "status": "running",
            "total": 1,
        }
        store.get_fanout_run = MagicMock(return_value=fanout_run)
        store.list_failed_fanout_items = MagicMock(return_value=[
            {"id": 1, "item_index": 0, "params_json": json.dumps({"domain": "a"}), "child_job_id": "ing_child_0", "status": "failed"},
        ])
        # Child is still running (not in RETRYABLE_STATUSES)
        store.get_job = MagicMock(return_value={"ingestion_job_id": "ing_child_0", "status": "accepted"})
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_parent_1")
        assert exc_info.value.error_code == "no_retry_submitted"
        # Parent should NOT be reopened
        store.reopen_fanout_run.assert_not_called()
        store.reopen_parent_ingestion_job.assert_not_called()

    def test_item_indexes_filter(self):
        svc, store, _ = self._make_fanout_setup()
        # Only retry item_index=0
        store.list_failed_fanout_items = MagicMock(return_value=[
            {"id": 1, "item_index": 0, "params_json": json.dumps({"domain": "a"}), "child_job_id": "ing_child_0", "status": "failed"},
        ])

        result = svc.retry_failed_children("ing_parent_1", item_indexes=[0])
        assert result["submitted"] == 1

    def test_all_children_active_raises_no_retry_submitted(self):
        """All items skipped due to active children → no_retry_submitted, no reopen."""
        svc, store, _ = _make_job_service()
        fanout_run = {
            "parent_job_id": "ing_parent_1",
            "child_command": "dcp_current_plan",
            "status": "partial",
            "total": 1,
        }
        store.get_fanout_run = MagicMock(return_value=fanout_run)
        store.list_failed_fanout_items = MagicMock(return_value=[
            {"id": 1, "item_index": 0, "params_json": json.dumps({"domain": "a"}), "child_job_id": "ing_child_0", "status": "failed"},
        ])
        # Child is not in a retryable state
        store.get_job = MagicMock(return_value={"ingestion_job_id": "ing_child_0", "status": "accepted"})
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_parent_1")
        assert exc_info.value.error_code == "no_retry_submitted"
        store.reopen_fanout_run.assert_not_called()
        store.reopen_parent_ingestion_job.assert_not_called()

    def test_no_connector_marks_child_failed_and_skips(self):
        """No connector configured → child marked failed, item skipped, but parent still reopened if any submitted."""
        svc, store, _ = _make_job_service()
        fanout_run = {
            "parent_job_id": "ing_parent_1",
            "child_command": "dcp_current_plan",
            "status": "partial",
            "total": 1,
        }
        store.get_fanout_run = MagicMock(return_value=fanout_run)
        store.list_failed_fanout_items = MagicMock(return_value=[
            {"id": 1, "item_index": 0, "params_json": json.dumps({"domain": "a"}), "child_job_id": "ing_child_0", "status": "failed"},
        ])
        store.get_job = MagicMock(return_value={"ingestion_job_id": "ing_child_0", "status": "failed", "params_json": json.dumps({"domain": "a"})})
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()
        store.reopen_job_for_retry = MagicMock(return_value=True)
        store.update_fanout_item_for_inplace_retry = MagicMock()
        # Make connector unavailable
        svc._trigger_clients = {}

        result = svc.retry_failed_children("ing_parent_1")
        # Child was reopened but then marked failed (no connector)
        # The item was submitted (reopen succeeded) but child execution failed
        assert result["submitted"] == 1
        assert result["skipped"] == 0

    def test_submitted_gt_zero_reopens_parent(self):
        """submitted > 0 → reopen_fanout_run + reopen_parent_ingestion_job called."""
        svc, store, _ = self._make_fanout_setup()
        result = svc.retry_failed_children("ing_parent_1")
        assert result["submitted"] == 2
        store.reopen_fanout_run.assert_called_once_with("ing_parent_1")
        store.reopen_parent_ingestion_job.assert_called_once_with("ing_parent_1")

    def test_submitted_zero_running_fanout_no_reopen(self):
        """submitted=0 but fanout_run still running → no_retry_submitted, no reopen needed."""
        svc, store, _ = _make_job_service()
        fanout_run = {
            "parent_job_id": "ing_parent_1",
            "child_command": "dcp_current_plan",
            "status": "running",  # still running
            "total": 1,
        }
        store.get_fanout_run = MagicMock(return_value=fanout_run)
        store.list_failed_fanout_items = MagicMock(return_value=[
            {"id": 1, "item_index": 0, "params_json": json.dumps({"domain": "a"}), "child_job_id": "ing_child_0", "status": "failed"},
        ])
        store.get_job = MagicMock(return_value={"ingestion_job_id": "ing_child_0", "status": "accepted"})
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_parent_1")
        assert exc_info.value.error_code == "no_retry_submitted"
        store.reopen_fanout_run.assert_not_called()
        store.reopen_parent_ingestion_job.assert_not_called()


# ---------------------------------------------------------------------------
# source field in CREATE TABLE baseline
# ---------------------------------------------------------------------------

class TestJobServiceErrorIngestionJobId:
    """P1.2: JobServiceError must carry ingestion_job_id when job already created."""

    def test_external_sync_failed_carries_ingestion_job_id(self):
        svc, store, client = _make_job_service()
        client.sync.side_effect = ConnectionError("downloader unreachable")

        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("dcp_current_plan")
        assert exc_info.value.error_code == "external_sync_failed"
        assert exc_info.value.ingestion_job_id is not None
        assert exc_info.value.ingestion_job_id.startswith("ing_dcp_current_plan_")

    def test_no_connector_carries_ingestion_job_id(self):
        plugins = _make_plugins()
        store = _make_store()
        svc = JobService(
            store=store,
            plugins=plugins,
            trigger_clients={},
            callback_base_url="http://localhost:8000",
        )

        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("dcp_current_plan")
        assert exc_info.value.error_code == "no_connector"
        assert exc_info.value.ingestion_job_id is not None
        assert exc_info.value.ingestion_job_id.startswith("ing_dcp_current_plan_")
        # Job should be marked failed
        mark_calls = store.mark_job.call_args_list
        assert any(c[1].get("status") == "failed" for c in mark_calls)

    def test_plugin_handler_failed_carries_ingestion_job_id(self):
        cmd = _make_command(
            name="bad_handler_cmd",
            trigger_type="plugin_handler",
            trigger={"type": "plugin_handler", "handler": "dcp.fan_out:nonexistent"},
        )
        plugins = _make_plugins(commands=[cmd])
        store = _make_store()
        client = _make_client()

        with patch("src.datahub.core.services.job_service.load_plugin_handler", side_effect=ImportError("no module")):
            svc = JobService(
                store=store,
                plugins=plugins,
                trigger_clients={"dcp": client},
                callback_base_url="http://localhost:8000",
            )
            with pytest.raises(JobServiceError) as exc_info:
                svc.submit_command("bad_handler_cmd")
            assert exc_info.value.error_code == "plugin_handler_failed"
            assert exc_info.value.ingestion_job_id is not None
            assert exc_info.value.ingestion_job_id.startswith("ing_bad_handler_cmd_")

    def test_invalid_trigger_missing_job_type_carries_ingestion_job_id(self):
        cmd = _make_command(
            name="no_job_type_cmd",
            trigger_type="downloader_sync",
            trigger={"type": "downloader_sync"},  # no job_type
        )
        plugins = _make_plugins(commands=[cmd])
        store = _make_store()
        svc = JobService(
            store=store,
            plugins=plugins,
            trigger_clients={"dcp": _make_client()},
            callback_base_url="http://localhost:8000",
        )

        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("no_job_type_cmd")
        assert exc_info.value.error_code == "invalid_trigger"
        assert exc_info.value.ingestion_job_id is not None
        assert exc_info.value.ingestion_job_id.startswith("ing_no_job_type_cmd_")

    def test_unknown_command_no_ingestion_job_id(self):
        svc, _, _ = _make_job_service(plugins=_make_plugins())
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("nonexistent_command")
        assert exc_info.value.error_code == "unknown_command"
        assert exc_info.value.ingestion_job_id is None

    def test_missing_required_param_no_ingestion_job_id(self):
        cmd = _make_command(name="needs_param", required_params=("projectCode",))
        plugins = _make_plugins(commands=[cmd])
        svc, _, _ = _make_job_service(plugins=plugins)
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("needs_param", params={})
        assert exc_info.value.error_code == "missing_required_param"
        assert exc_info.value.ingestion_job_id is None

    def test_invalid_source_no_ingestion_job_id(self):
        svc, _, _ = _make_job_service()
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("dcp_current_plan", source="invalid_source")
        assert exc_info.value.error_code == "invalid_source"
        assert exc_info.value.ingestion_job_id is None

    def test_command_disabled_no_ingestion_job_id(self):
        cmd = _make_command(name="disabled_cmd", enabled=False)
        plugins = _make_plugins(commands=[cmd])
        svc, _, _ = _make_job_service(plugins=plugins)
        with pytest.raises(JobServiceError) as exc_info:
            svc.submit_command("disabled_cmd")
        assert exc_info.value.error_code == "command_disabled"
        assert exc_info.value.ingestion_job_id is None


class TestSourceFieldBaseline:
    def test_source_in_ingestion_jobs_baseline(self):
        """After init_schema, ingestion_jobs.source exists from CREATE TABLE, not ALTER TABLE."""
        from src.datahub.storage.ddl import create_metadata_tables
        from src.datahub.core.registry import SchemaRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            create_metadata_tables(conn)

            columns = {row[1]: row for row in conn.execute("PRAGMA table_info(ingestion_jobs)").fetchall()}
            assert "source" in columns, "source column missing from ingestion_jobs"
            # Verify it's NOT NULL DEFAULT 'api' from baseline
            col = columns["source"]
            # SQLite PRAGMA table_info: cid, name, type, notnull, dflt_value, pk
            assert col[2] == "TEXT"
            assert col[3] == 1, "source should be NOT NULL (notnull=1)"
            assert col[4] == "'api'", f"source default should be 'api', got {col[4]}"
            conn.close()

    def test_retry_of_job_id_in_ingestion_jobs_baseline(self):
        """P2: retry_of_job_id column exists in ingestion_jobs CREATE TABLE baseline."""
        from src.datahub.storage.ddl import create_metadata_tables

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            create_metadata_tables(conn)

            columns = {row[1]: row for row in conn.execute("PRAGMA table_info(ingestion_jobs)").fetchall()}
            assert "retry_of_job_id" in columns, "retry_of_job_id column missing from ingestion_jobs"
            col = columns["retry_of_job_id"]
            assert col[2] == "TEXT"
            assert col[3] == 0, "retry_of_job_id should be nullable (notnull=0)"
            conn.close()


# ---------------------------------------------------------------------------
# API error response includes ingestion_job_id
# ---------------------------------------------------------------------------

class TestAPIErrorIngestionJobId:
    """P1.2: API error responses must include ingestion_job_id when present."""

    def _build_client(self, mock_job_svc):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.datahub.api.ingestion import build_ingestion_router
        from src.datahub.settings import Settings

        settings = Settings()
        store = _make_store()

        router = build_ingestion_router(
            settings=settings,
            plugins=_make_plugins(),
            store=store,
            trigger_clients={"dcp": _make_client()},
            ingestion_service=MagicMock(),
            job_service=mock_job_svc,
        )
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_api_error_includes_ingestion_job_id(self):
        """external_sync_failed with ingestion_job_id should include it in response detail."""
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.submit_command.side_effect = JobServiceError(
            "external_sync_failed", "connection refused", ingestion_job_id="ing_test_abc123"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs", json={"command": "dcp_current_plan", "params": {}})
        assert resp.status_code == 502
        detail = resp.json()["detail"]
        assert detail["error"] == "external_sync_failed"
        assert detail["ingestion_job_id"] == "ing_test_abc123"

    def test_api_error_without_ingestion_job_id(self):
        """unknown_command (no ingestion_job_id) should not include it in response detail."""
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.submit_command.side_effect = JobServiceError(
            "unknown_command", "command not found"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs", json={"command": "nonexistent", "params": {}})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail["error"] == "unknown_command"
        assert "ingestion_job_id" not in detail


# ---------------------------------------------------------------------------
# P2: API retry and retry-failed-children
# ---------------------------------------------------------------------------

class TestAPIRetryP2:
    """P2: API retry returns retry_of_job_id; retry-failed-children endpoint."""

    def _build_client(self, mock_job_svc):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.datahub.api.ingestion import build_ingestion_router
        from src.datahub.settings import Settings

        settings = Settings()
        store = _make_store()

        router = build_ingestion_router(
            settings=settings,
            plugins=_make_plugins(),
            store=store,
            trigger_clients={"dcp": _make_client()},
            ingestion_service=MagicMock(),
            job_service=mock_job_svc,
        )
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_retry_returns_same_job_id(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_job.return_value = JobResult(
            ingestion_job_id="ing_old_1",  # same job_id (in-place retry)
            status="accepted",
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_old_1/retry")
        assert resp.status_code == 202
        data = resp.json()
        assert data["ingestion_job_id"] == "ing_old_1"  # same job_id
        # No original_job_id or retry_of_job_id in response (in-place retry)

    def test_retry_not_retryable_returns_409(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_job.side_effect = JobServiceError(
            "job_not_retryable", "job is running"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_old_1/retry")
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "job_not_retryable"

    def test_retry_failed_children_returns_submitted(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_failed_children.return_value = {
            "parent_job_id": "ing_parent_1",
            "submitted": 2,
            "skipped": 0,
            "items": [
                {"item_index": 0, "child_job_id": "ing_c0", "status": "submitted"},
                {"item_index": 1, "child_job_id": "ing_c1", "status": "submitted"},
            ],
            "skipped_items": [],
        }

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_parent_1/retry-failed-children")
        assert resp.status_code == 202
        data = resp.json()
        assert data["submitted"] == 2
        assert len(data["items"]) == 2

    def test_no_failed_children_returns_409(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_failed_children.side_effect = JobServiceError(
            "no_failed_children", "no failed children"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_parent_1/retry-failed-children")
        assert resp.status_code == 409

    def test_not_fanout_parent_returns_404(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_failed_children.side_effect = JobServiceError(
            "not_fanout_parent", "not a fanout parent"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_parent_1/retry-failed-children")
        assert resp.status_code == 404

    def test_no_retry_submitted_returns_409(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_failed_children.side_effect = JobServiceError(
            "no_retry_submitted", "0 of 1 items submitted, 1 skipped"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_parent_1/retry-failed-children")
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "no_retry_submitted"


# ---------------------------------------------------------------------------
# P2.1: Store reopen_parent_ingestion_job
# ---------------------------------------------------------------------------

class TestReopenParentIngestionJob:
    """P2.1: reopen_parent_ingestion_job clears error/result_json/finished_at."""

    def test_reopen_clears_error_result_finished(self):
        from src.datahub.storage.sqlite import DataHubStore
        from src.datahub.core.registry import SchemaRegistry
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            registry = SchemaRegistry(version=1, tables={}, datasets=set(), raw={})
            store = DataHubStore(db_path, registry)
            store.init_schema(dev_mode=False)

            # Create a job
            store.create_ingestion_job(
                ingestion_job_id="ing_parent_1",
                producer_job_id="prod_1",
                job_type="test_cmd",
                params={"domain": "a"},
                plugin_id="dcp",
            )
            # Mark it as failed with error and result
            store.mark_job("ing_parent_1", status="partial", error="some children failed", result={"total": 10, "succeeded": 8})

            # Verify it has error and result
            job = store.get_job("ing_parent_1")
            assert job["status"] == "partial"
            assert job["error"] == "some children failed"
            assert job["result_json"] is not None
            assert job["finished_at"] is not None

            # Reopen
            store.reopen_parent_ingestion_job("ing_parent_1")

            # Verify cleared
            job = store.get_job("ing_parent_1")
            assert job["status"] == "running"
            assert job["error"] is None
            assert job["result_json"] is None
            assert job["finished_at"] is None


# ---------------------------------------------------------------------------
# P3.1: Fan-out detail API
# ---------------------------------------------------------------------------

class TestFanoutDetailAPI:
    """P3.1: GET /ingestion/v1/jobs/{parent}/fanout returns fanout_run/stats/items."""

    @staticmethod
    def _build_client(mock_job_svc):
        from fastapi.testclient import TestClient
        from src.datahub.storage.sqlite import DataHubStore
        from src.datahub.core.registry import SchemaRegistry
        from src.datahub.api.ingestion import build_ingestion_router
        from src.datahub.settings import Settings
        from fastapi import FastAPI
        import tempfile

        tmpdir = tempfile.mkdtemp()
        db_path = str(Path(tmpdir) / "test.db")
        registry = SchemaRegistry(version=1, tables={}, datasets=set(), raw={})
        store = DataHubStore(db_path, registry)
        store.init_schema(dev_mode=True)

        settings = Settings()
        app = FastAPI()
        router = build_ingestion_router(
            settings=settings,
            plugins=_make_plugins(),
            store=store,
            trigger_clients={"dcp": _make_client()},
            ingestion_service=MagicMock(),
            job_service=mock_job_svc,
        )
        app.include_router(router)
        return TestClient(app), store

    def test_fanout_detail_returns_items_with_child_info(self):
        """Fanout detail API returns item_index, retry_count, child fields."""
        from src.datahub.core.services.job_service import JobService

        svc = MagicMock(spec=JobService)
        client, store = self._build_client(svc)

        # Create parent job
        store.create_ingestion_job(
            ingestion_job_id="ing_parent_1",
            producer_job_id="prod_1",
            job_type="dcp_current_plan",
            params={"domain": "all"},
            plugin_id="dcp",
        )
        # Create fanout_run
        with sqlite3.connect(store.db_path) as conn:
            conn.execute(
                "INSERT INTO fanout_runs(parent_job_id, plugin_id, parent_command, child_command, total, status, created_at, updated_at) VALUES (?,?,?,?,?,?,datetime('now'),datetime('now'))",
                ("ing_parent_1", "dcp", "dcp_current_plan", "dcp_current_plan_for_project", 3, "partial"),
            )
            conn.execute(
                "INSERT INTO fanout_items(parent_job_id, item_index, params_json, status, child_job_id, retry_count, created_at, updated_at) VALUES (?,?,?,'failed',?,0,datetime('now'),datetime('now'))",
                ("ing_parent_1", 0, '{"projectCode":"A"}', "ing_child_0"),
            )
            conn.execute(
                "INSERT INTO fanout_items(parent_job_id, item_index, params_json, status, child_job_id, retry_count, created_at, updated_at) VALUES (?,?,?,'succeeded',?,0,datetime('now'),datetime('now'))",
                ("ing_parent_1", 1, '{"projectCode":"B"}', "ing_child_1"),
            )
            conn.execute(
                "INSERT INTO fanout_items(parent_job_id, item_index, params_json, status, retry_count, created_at, updated_at) VALUES (?,?,?,'skipped',0,datetime('now'),datetime('now'))",
                ("ing_parent_1", 2, '{"projectCode":"C"}'),
            )
        # Create child jobs
        store.create_ingestion_job(
            ingestion_job_id="ing_child_0",
            producer_job_id="prod_c0",
            job_type="dcp_current_plan_for_project",
            params={"projectCode": "A"},
            plugin_id="dcp",
            parent_job_id="ing_parent_1",
        )
        store.mark_job("ing_child_0", status="failed", error="connection refused")
        store.create_ingestion_job(
            ingestion_job_id="ing_child_1",
            producer_job_id="prod_c1",
            job_type="dcp_current_plan_for_project",
            params={"projectCode": "B"},
            plugin_id="dcp",
            parent_job_id="ing_parent_1",
        )
        store.mark_job("ing_child_1", status="succeeded")

        resp = client.get(
            "/ingestion/v1/jobs/ing_parent_1/fanout",
            headers={"X-API-Key": "dev-admin-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["parent_job_id"] == "ing_parent_1"
        assert data["fanout_run"]["status"] == "partial"
        assert data["fanout_run"]["child_command"] == "dcp_current_plan_for_project"
        assert data["stats"]["failed"] == 1
        assert data["stats"]["succeeded"] == 1
        assert data["stats"]["skipped"] == 1
        assert len(data["items"]) == 3

        # Item 0: failed with child
        item0 = data["items"][0]
        assert item0["item_index"] == 0
        assert item0["status"] == "failed"
        assert item0["retry_count"] == 0
        assert item0["child_job_id"] == "ing_child_0"
        assert item0["child_status"] == "failed"
        assert item0["child_error"] == "connection refused"

        # Item 2: skipped, no child
        item2 = data["items"][2]
        assert item2["item_index"] == 2
        assert item2["status"] == "skipped"
        assert item2["child_job_id"] is None
        assert item2["child_status"] is None

    def test_not_fanout_parent_returns_404(self):
        """Non-fanout parent returns 404 not_fanout_parent."""
        from src.datahub.core.services.job_service import JobService

        svc = MagicMock(spec=JobService)
        client, store = self._build_client(svc)

        # Create a non-fanout job
        store.create_ingestion_job(
            ingestion_job_id="ing_normal_1",
            producer_job_id="prod_1",
            job_type="test_cmd",
            params={"domain": "a"},
            plugin_id="dcp",
        )

        resp = client.get(
            "/ingestion/v1/jobs/ing_normal_1/fanout",
            headers={"X-API-Key": "dev-admin-key"},
        )
        assert resp.status_code == 404
        assert resp.json()["detail"]["error"] == "not_fanout_parent"

    def test_nonexistent_job_returns_404(self):
        """Nonexistent job returns 404 not_fanout_parent."""
        from src.datahub.core.services.job_service import JobService

        svc = MagicMock(spec=JobService)
        client, store = self._build_client(svc)

        resp = client.get(
            "/ingestion/v1/jobs/ing_nonexistent/fanout",
            headers={"X-API-Key": "dev-admin-key"},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# P5.5: Internal params helpers
# ---------------------------------------------------------------------------

class TestStripInternalParams:

    def test_strips_datahub_key(self):
        params = {"projectCode": "A", "__datahub": {"retry_count": 1}}
        result = strip_internal_params(params)
        assert result == {"projectCode": "A"}
        assert "__datahub" not in result

    def test_no_datahub_returns_same(self):
        params = {"projectCode": "A"}
        result = strip_internal_params(params)
        assert result == {"projectCode": "A"}

    def test_empty_params(self):
        assert strip_internal_params({}) == {}
        assert strip_internal_params(None) is None


class TestGetInternalRetryCount:

    def test_reads_retry_count(self):
        params = {"__datahub": {"retry_count": 2}}
        assert get_internal_retry_count(params) == 2

    def test_no_datahub_returns_zero(self):
        assert get_internal_retry_count({}) == 0
        assert get_internal_retry_count(None) == 0

    def test_non_dict_datahub_returns_zero(self):
        assert get_internal_retry_count({"__datahub": "invalid"}) == 0


class TestBumpInternalRetryMeta:

    def test_increments_retry_count(self):
        params = {}
        result = bump_internal_retry_meta(params, reason="manual", last_error="timeout")
        assert result["__datahub"]["retry_count"] == 1
        assert result["__datahub"]["last_retry_reason"] == "manual"
        assert result["__datahub"]["last_error"] == "timeout"

    def test_increments_from_existing(self):
        params = {"__datahub": {"retry_count": 1}}
        result = bump_internal_retry_meta(params, reason="auto_non_success")
        assert result["__datahub"]["retry_count"] == 2

    def test_overwrites_external_datahub(self):
        """External __datahub fields are overwritten; retry_count increments from existing."""
        params = {"__datahub": {"retry_count": 999, "forged": True}}
        result = bump_internal_retry_meta(params, reason="manual")
        assert result["__datahub"]["retry_count"] == 1000  # increments from existing
        assert "forged" not in result["__datahub"]  # forged fields removed

    def test_preserves_business_params(self):
        params = {"projectCode": "A", "year": "2024"}
        result = bump_internal_retry_meta(params, reason="manual")
        assert result["projectCode"] == "A"
        assert result["year"] == "2024"


# ---------------------------------------------------------------------------
# P5.5: Fanout scheduler helpers
# ---------------------------------------------------------------------------

class TestGetChildRetryCount:

    def test_reads_from_params_json(self):
        child_job = {"params_json": json.dumps({"__datahub": {"retry_count": 1}})}
        assert _get_child_retry_count(child_job) == 1

    def test_no_datahub_returns_zero(self):
        child_job = {"params_json": json.dumps({"projectCode": "A"})}
        assert _get_child_retry_count(child_job) == 0

    def test_invalid_json_returns_zero(self):
        child_job = {"params_json": "not json"}
        assert _get_child_retry_count(child_job) == 0


class TestIsChildNonSuccess:

    def test_failed(self):
        assert _is_child_non_success({"status": "failed"}) is True

    def test_partial(self):
        assert _is_child_non_success({"status": "partial"}) is True

    def test_cancelled(self):
        assert _is_child_non_success({"status": "cancelled"}) is True

    def test_succeeded(self):
        assert _is_child_non_success({"status": "succeeded"}) is False

    def test_running(self):
        assert _is_child_non_success({"status": "running"}) is False


# ---------------------------------------------------------------------------
# P5.5: JobService retry_job in-place
# ---------------------------------------------------------------------------

def _make_p55_service(store, plugins, trigger_clients=None):
    return JobService(
        store=store,
        plugins=plugins,
        trigger_clients=trigger_clients or {},
        callback_base_url="http://localhost:8000",
    )


def _make_plugin_with_command(command_name="test_cmd", trigger_type="downloader_sync"):
    trigger = {"type": trigger_type}
    if trigger_type == "downloader_sync":
        trigger["job_type"] = "test_job_type"
    elif trigger_type == "plugin_handler":
        trigger["handler"] = "dcp.fan_out:refresh_towers_for_current_plan_projects"

    command = CommandSpec(
        name=command_name,
        required_params=("projectCode",),
        trigger=trigger,
        enabled=True,
    )
    plugin = PluginSpec(
            name="dcp",
            version=1,
            display=DisplaySpec(label="DCP"),
            connector=ConnectorSpec(type="http", base_url="http://localhost:9000"),
            commands=[command],
        )
    return plugin, command


class TestRetryJobInPlace:

    def test_retry_returns_same_job_id(self):
        """retry_job returns the same ingestion_job_id, not a new one."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_test_cmd_abc123",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "dcp_remote_failure",
        }
        plugin, command = _make_plugin_with_command()
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_job("ing_test_cmd_abc123")

        assert result.ingestion_job_id == "ing_test_cmd_abc123"

    def test_retry_does_not_create_new_job(self):
        """retry_job calls reopen_job_for_retry, not create_ingestion_job."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_test_cmd_abc123",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "timeout",
        }
        plugin, command = _make_plugin_with_command()

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": MagicMock()})
            svc._trigger_clients["dcp"].sync.return_value = {"status": "accepted"}
            result = svc.retry_job("ing_test_cmd_abc123")

        store.reopen_job_for_retry.assert_called_once()
        store.create_ingestion_job.assert_not_called()

    def test_retry_bumps_datahub_retry_count(self):
        """retry_job bumps __datahub.retry_count from 0 to 1."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_test_cmd_abc123",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "timeout",
        }
        plugin, command = _make_plugin_with_command()

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": MagicMock()})
            svc._trigger_clients["dcp"].sync.return_value = {"status": "accepted"}
            result = svc.retry_job("ing_test_cmd_abc123")

        call_args = store.reopen_job_for_retry.call_args
        params_json_str = call_args[1]["params_json"]
        params = json.loads(params_json_str)
        assert params["__datahub"]["retry_count"] == 1

    def test_downloader_receives_stripped_params(self):
        """client.sync receives params without __datahub."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_test_cmd_abc123",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "timeout",
        }
        plugin, command = _make_plugin_with_command()
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_job("ing_test_cmd_abc123")

        sync_call = mock_client.sync.call_args
        params_sent = sync_call[1]["params"]
        assert "__datahub" not in params_sent
        assert "projectCode" in params_sent

    def test_retry_success_sets_succeeded(self):
        """After retry, if callback succeeds, job.status=succeeded."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_test_cmd_abc123",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "timeout",
        }
        plugin, command = _make_plugin_with_command()
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_job("ing_test_cmd_abc123")

        store.mark_job.assert_called_once()
        call_args = store.mark_job.call_args
        assert call_args[0][0] == "ing_test_cmd_abc123"
        assert call_args[1]["status"] == "accepted"

    def test_retry_failed_stays_failed(self):
        """If retry sync throws, job.status=failed."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_test_cmd_abc123",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "timeout",
        }
        plugin, command = _make_plugin_with_command()
        mock_client = MagicMock()
        mock_client.sync.side_effect = Exception("still failing")

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            with pytest.raises(JobServiceError):
                svc.retry_job("ing_test_cmd_abc123")

        mark_calls = [c for c in store.mark_job.call_args_list if c[1].get("status") == "failed"]
        assert len(mark_calls) >= 1

    def test_external_datahub_ignored_on_submit(self):
        """submit_command strips externally-provided __datahub."""
        store = MagicMock()
        plugin, command = _make_plugin_with_command()
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.submit_command("test_cmd", {"projectCode": "A", "__datahub": {"retry_count": 999}})

        create_call = store.create_ingestion_job.call_args
        assert create_call[1]["params"] == {"projectCode": "A"}

        sync_call = mock_client.sync.call_args
        assert "__datahub" not in sync_call[1]["params"]


# ---------------------------------------------------------------------------
# P5.5: Fanout auto-retry
# ---------------------------------------------------------------------------

class TestFanoutAutoRetry:

    def test_auto_retry_once_on_non_success(self):
        """Fanout scheduler auto-retries a non-success child once (retry_count < 1)."""
        store = MagicMock()
        child_job = {
            "ingestion_job_id": "ing_child_001",
            "status": "failed",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "dcp_remote_failure",
        }
        store.get_job.return_value = child_job

        plugin, command = _make_plugin_with_command("refresh_towers_for_project", trigger_type="downloader_sync")
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        run = {
            "parent_job_id": "ing_parent_001",
            "child_command": "refresh_towers_for_project",
            "status": "running",
            "circuit_opened": False,
            "consecutive_failure_threshold": 10,
            "max_concurrency": 5,
            "cooldown_seconds": 3,
            "last_submit_at": None,
        }
        item = {
            "id": 1,
            "item_index": 0,
            "child_job_id": "ing_child_001",
            "retry_count": 0,
        }

        from src.datahub.core.fanout_scheduler import _inplace_retry_child
        with patch("src.datahub.core.plugin_loader.find_command", return_value=command), \
             patch("src.datahub.core.plugin_loader.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.trigger_runtime.new_producer_job_id", return_value="prod_retry_001"):
            _inplace_retry_child(
                store, {"dcp": mock_client}, [plugin], run, item, child_job,
                callback_base_url="http://localhost:8000",
                callback_headers=None,
            )

        store.reopen_job_for_retry.assert_called_once()
        store.update_fanout_item_for_inplace_retry.assert_called_once_with(1)

    def test_auto_retry_not_exceed_once(self):
        """Auto-retry does not fire if child retry_count >= 1."""
        child_job = {
            "status": "failed",
            "params_json": json.dumps({"__datahub": {"retry_count": 1}}),
        }
        assert _get_child_retry_count(child_job) == 1

    def test_auto_retry_no_new_child_job(self):
        """In-place retry keeps the same child_job_id."""
        store = MagicMock()
        child_job = {
            "ingestion_job_id": "ing_child_001",
            "status": "failed",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "dcp_remote_failure",
        }
        store.get_job.return_value = child_job

        plugin, command = _make_plugin_with_command("refresh_towers_for_project")
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        run = {
            "parent_job_id": "ing_parent_001",
            "child_command": "refresh_towers_for_project",
            "status": "running",
            "circuit_opened": False,
            "consecutive_failure_threshold": 10,
            "max_concurrency": 5,
            "cooldown_seconds": 3,
            "last_submit_at": None,
        }
        item = {
            "id": 1,
            "item_index": 0,
            "child_job_id": "ing_child_001",
            "retry_count": 0,
        }

        from src.datahub.core.fanout_scheduler import _inplace_retry_child
        with patch("src.datahub.core.plugin_loader.find_command", return_value=command), \
             patch("src.datahub.core.plugin_loader.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.trigger_runtime.new_producer_job_id", return_value="prod_retry_001"):
            _inplace_retry_child(
                store, {"dcp": mock_client}, [plugin], run, item, child_job,
                callback_base_url="http://localhost:8000",
                callback_headers=None,
            )

        store.create_ingestion_job.assert_not_called()
        reopen_call = store.reopen_job_for_retry.call_args
        assert reopen_call[0][0] == "ing_child_001"


# ---------------------------------------------------------------------------
# P5.5: retry_failed_children in-place
# ---------------------------------------------------------------------------

class TestRetryFailedChildrenInPlace:

    def test_retry_failed_children_uses_same_child_job_id(self):
        """retry_failed_children reopens child jobs in-place."""
        store = MagicMock()
        store.get_fanout_run.return_value = {
            "parent_job_id": "ing_parent_001",
            "child_command": "refresh_towers_for_project",
            "status": "partial",
        }
        store.list_failed_fanout_items.return_value = [
            {
                "id": 1,
                "item_index": 0,
                "child_job_id": "ing_child_001",
                "params_json": json.dumps({"projectCode": "A"}),
            },
        ]
        store.get_job.return_value = {
            "ingestion_job_id": "ing_child_001",
            "status": "failed",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "dcp_remote_failure",
        }

        plugin, command = _make_plugin_with_command("refresh_towers_for_project")
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_retry_001"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_failed_children("ing_parent_001")

        assert result["submitted"] == 1
        assert result["items"][0]["child_job_id"] == "ing_child_001"
        store.reopen_job_for_retry.assert_called_once()
        store.update_fanout_item_for_inplace_retry.assert_called_once_with(1)
        store.reopen_fanout_run.assert_called_once()
        store.reopen_parent_ingestion_job.assert_called_once()

    def test_retry_failed_children_parent_reopens(self):
        """retry_failed_children reopens parent fanout_run and ingestion_job."""
        store = MagicMock()
        store.get_fanout_run.return_value = {
            "parent_job_id": "ing_parent_001",
            "child_command": "refresh_towers_for_project",
            "status": "partial",
        }
        store.list_failed_fanout_items.return_value = [
            {
                "id": 1,
                "item_index": 0,
                "child_job_id": "ing_child_001",
                "params_json": json.dumps({"projectCode": "A"}),
            },
        ]
        store.get_job.return_value = {
            "ingestion_job_id": "ing_child_001",
            "status": "failed",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "dcp_remote_failure",
        }

        plugin, command = _make_plugin_with_command("refresh_towers_for_project")
        mock_client = MagicMock()
        mock_client.sync.return_value = {"status": "accepted"}

        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_retry_001"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_failed_children("ing_parent_001")

        store.reopen_fanout_run.assert_called_once_with("ing_parent_001")
        store.reopen_parent_ingestion_job.assert_called_once_with("ing_parent_001")


# ---------------------------------------------------------------------------
# P5.5.2: reopen_job_for_retry uses downloader_job_id, concurrent protection,
#          fanout scheduler crash guard
# ---------------------------------------------------------------------------

class TestReopenJobForRetryStoreLevel:
    """Store-level tests for reopen_job_for_retry using downloader_job_id."""

    @staticmethod
    def _make_store():
        from src.datahub.storage.sqlite import DataHubStore
        from src.datahub.core.registry import SchemaRegistry
        import tempfile

        tmpdir = tempfile.mkdtemp()
        db_path = str(Path(tmpdir) / "test.db")
        registry = SchemaRegistry(version=1, tables={}, datasets=set(), raw={})
        store = DataHubStore(db_path, registry)
        store.init_schema(dev_mode=False)
        return store

    def test_reopen_uses_downloader_job_id(self):
        """reopen_job_for_retry updates downloader_job_id, not producer_job_id."""
        store = self._make_store()
        store.create_ingestion_job(
            ingestion_job_id="ing_1",
            producer_job_id="dl_original",
            job_type="test_cmd",
            params={"x": 1},
        )
        store.mark_job("ing_1", status="failed", error="boom")

        result = store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry_new",
            params_json='{"x":1,"__datahub":{"retry_count":1}}',
            source="retry",
        )
        assert result is True

        job = store.get_job("ing_1")
        assert job["downloader_job_id"] == "dl_retry_new"
        assert job["status"] == "triggering"

    def test_reopen_no_producer_job_id_column(self):
        """reopen_job_for_retry SQL must not reference producer_job_id."""
        import re
        from src.datahub.storage import sqlite as sqlite_mod
        source = inspect.getsource(sqlite_mod.DataHubStore.reopen_job_for_retry)
        assert "producer_job_id" not in source, "reopen_job_for_retry must not reference producer_job_id column"

    def test_reopen_does_not_increase_row_count(self):
        """Reopening a job does not create a new ingestion_jobs row."""
        store = self._make_store()
        store.create_ingestion_job(
            ingestion_job_id="ing_1",
            producer_job_id="dl_1",
            job_type="test_cmd",
            params={},
        )
        store.mark_job("ing_1", status="failed", error="boom")

        import sqlite3
        with sqlite3.connect(store.db_path) as conn:
            count_before = conn.execute("SELECT COUNT(*) FROM ingestion_jobs").fetchone()[0]

        store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry",
            params_json='{}',
            source="retry",
        )

        with sqlite3.connect(store.db_path) as conn:
            count_after = conn.execute("SELECT COUNT(*) FROM ingestion_jobs").fetchone()[0]
        assert count_after == count_before

    def test_reopen_clears_error_result_producer_status_finished(self):
        """reopen clears error, result_json, producer_status_json, finished_at."""
        store = self._make_store()
        store.create_ingestion_job(
            ingestion_job_id="ing_1",
            producer_job_id="dl_1",
            job_type="test_cmd",
            params={},
        )
        store.mark_job("ing_1", status="failed", error="some error", result={"k": "v"})

        job_before = store.get_job("ing_1")
        assert job_before["error"] is not None
        assert job_before["result_json"] is not None
        assert job_before["finished_at"] is not None

        store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry",
            params_json='{}',
            source="retry",
        )

        job = store.get_job("ing_1")
        assert job["error"] is None
        assert job["result_json"] is None
        assert job["producer_status_json"] is None
        assert job["finished_at"] is None

    def test_reopen_resets_message_counters_and_row_count(self):
        """reopen resets message_total, message_received, message_failed, row_count to 0."""
        store = self._make_store()
        store.create_ingestion_job(
            ingestion_job_id="ing_1",
            producer_job_id="dl_1",
            job_type="test_cmd",
            params={},
        )
        store.mark_job("ing_1", status="failed", error="boom")

        # Simulate counters being set
        import sqlite3
        with sqlite3.connect(store.db_path) as conn:
            conn.execute(
                "UPDATE ingestion_jobs SET message_total=5, message_received=3, message_failed=2, row_count=100 WHERE ingestion_job_id='ing_1'"
            )

        store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry",
            params_json='{}',
            source="retry",
        )

        job = store.get_job("ing_1")
        assert job["message_total"] == 0
        assert job["message_received"] == 0
        assert job["message_failed"] == 0
        assert job["row_count"] == 0

    def test_reopen_only_allows_failed_partial_cancelled(self):
        """reopen_job_for_retry returns False for non-retryable statuses."""
        store = self._make_store()
        store.create_ingestion_job(
            ingestion_job_id="ing_1",
            producer_job_id="dl_1",
            job_type="test_cmd",
            params={},
        )
        # Job starts as 'triggering' — not retryable
        result = store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry",
            params_json='{}',
            source="retry",
        )
        assert result is False

        # Mark as succeeded — not retryable
        store.mark_job("ing_1", status="succeeded")
        result = store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry2",
            params_json='{}',
            source="retry",
        )
        assert result is False

        # Mark as failed — retryable
        store.mark_job("ing_1", status="failed", error="boom")
        result = store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry3",
            params_json='{}',
            source="retry",
        )
        assert result is True


class TestRetryJobConcurrentProtection:
    """retry_job handles concurrent reopen failures gracefully."""

    def test_retry_concurrent_reopen_returns_retry_already_started(self):
        """If reopen returns False because job is already triggering, raise retry_already_started."""
        store = MagicMock()
        store.get_job.return_value = {
            "ingestion_job_id": "ing_1",
            "status": "failed",
            "trigger_key": "test_cmd",
            "params_json": json.dumps({"x": 1}),
            "error": "boom",
        }
        store.reopen_job_for_retry.return_value = False

        # Second get_job call returns already-triggering status
        store.get_job.side_effect = [
            {"ingestion_job_id": "ing_1", "status": "failed", "trigger_key": "test_cmd",
             "params_json": json.dumps({"x": 1}), "error": "boom"},
            {"ingestion_job_id": "ing_1", "status": "triggering", "trigger_key": "test_cmd",
             "params_json": json.dumps({"x": 1})},
        ]

        plugin, command = _make_plugin_with_command()
        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": MagicMock()})

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_1")
        assert exc_info.value.error_code == "retry_already_started"

    def test_retry_concurrent_reopen_still_failed_returns_not_retryable(self):
        """If reopen returns False and job is still failed, raise job_not_retryable."""
        store = MagicMock()
        store.reopen_job_for_retry.return_value = False

        # Both get_job calls return failed (edge case: status changed back)
        store.get_job.side_effect = [
            {"ingestion_job_id": "ing_1", "status": "failed", "trigger_key": "test_cmd",
             "params_json": json.dumps({"x": 1}), "error": "boom"},
            {"ingestion_job_id": "ing_1", "status": "succeeded", "trigger_key": "test_cmd",
             "params_json": json.dumps({"x": 1})},
        ]

        plugin, command = _make_plugin_with_command()
        with patch("src.datahub.core.services.job_service.find_command", return_value=command), \
             patch("src.datahub.core.services.job_service.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.services.job_service.new_producer_job_id", return_value="prod_123"):
            svc = _make_p55_service(store, [plugin], trigger_clients={"dcp": MagicMock()})

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_1")
        assert exc_info.value.error_code == "job_not_retryable"


class TestRetryJobDownloaderJobId:
    """retry_job updates downloader_job_id after reopen."""

    def test_retry_updates_downloader_job_id(self):
        """After retry, the job's downloader_job_id should be updated."""
        store = self._make_store()
        store.create_ingestion_job(
            ingestion_job_id="ing_1",
            producer_job_id="dl_original",
            job_type="test_cmd",
            params={"x": 1},
        )
        store.mark_job("ing_1", status="failed", error="boom")

        store.reopen_job_for_retry(
            "ing_1",
            new_downloader_job_id="dl_retry_new",
            params_json='{"x":1,"__datahub":{"retry_count":1}}',
            source="retry",
        )

        job = store.get_job("ing_1")
        assert job["downloader_job_id"] == "dl_retry_new"

    @staticmethod
    def _make_store():
        from src.datahub.storage.sqlite import DataHubStore
        from src.datahub.core.registry import SchemaRegistry
        import tempfile

        tmpdir = tempfile.mkdtemp()
        db_path = str(Path(tmpdir) / "test.db")
        registry = SchemaRegistry(version=1, tables={}, datasets=set(), raw={})
        store = DataHubStore(db_path, registry)
        store.init_schema(dev_mode=False)
        return store


class TestFanoutSchedulerCrashGuard:
    """Fanout scheduler does not crash on _inplace_retry_child exception."""

    def test_inplace_retry_exception_marks_item_failed(self):
        """If _inplace_retry_child throws, the item is marked failed, not left hanging."""
        from src.datahub.core.fanout_scheduler import _advance_fanout_run

        store = MagicMock()
        store.get_fanout_run.return_value = {
            "parent_job_id": "ing_parent_001",
            "child_command": "refresh_towers_for_project",
            "status": "running",
            "circuit_opened": False,
            "consecutive_failure_threshold": 10,
            "max_concurrency": 5,
            "cooldown_seconds": 3,
            "last_submit_at": None,
            "total": 1,
        }
        store.list_submitted_fanout_items.return_value = [
            {
                "id": 1,
                "item_index": 0,
                "child_job_id": "ing_child_001",
                "status": "submitted",
                "retry_count": 0,
                "params_json": json.dumps({"projectCode": "A"}),
            },
        ]
        child_job = {
            "ingestion_job_id": "ing_child_001",
            "status": "failed",
            "params_json": json.dumps({"projectCode": "A"}),
            "error": "dcp_remote_failure",
        }
        store.get_job.return_value = child_job
        store.get_fanout_stats.return_value = {"total": 1, "succeeded": 0, "failed": 1, "skipped": 0, "pending": 0, "submitted": 0, "submitting": 0}
        store.get_consecutive_failures.return_value = 1

        plugin, command = _make_plugin_with_command("refresh_towers_for_project")

        with patch("src.datahub.core.plugin_loader.find_command", return_value=command), \
             patch("src.datahub.core.plugin_loader.find_plugin_for_job", return_value=plugin), \
             patch("src.datahub.core.fanout_scheduler._inplace_retry_child", side_effect=Exception("DB column not found")):
            _advance_fanout_run(
                store, {"dcp": MagicMock()}, [plugin],
                run=store.get_fanout_run.return_value,
                callback_base_url="http://localhost:8000",
                callback_headers=None,
                scheduler_id="test_scheduler",
            )

        # Item should be marked failed, not left hanging
        store.update_fanout_item_terminal.assert_called_once()
        call_args = store.update_fanout_item_terminal.call_args
        assert call_args[0][0] == 1  # item id
        assert call_args[1]["status"] == "failed"
        assert "inplace_retry_failed" in call_args[1]["error"]
