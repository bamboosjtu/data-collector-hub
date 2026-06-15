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

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.datahub.core.services.job_service import JobService, JobServiceError, JobResult, RETRYABLE_STATUSES
from src.datahub.core.specs import CommandSpec, PluginSpec, DisplaySpec, ConnectorSpec


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
    def test_retry_failed_job_creates_new_job_with_same_command_and_params(self):
        svc, store, client = _make_job_service()
        original = {
            "ingestion_job_id": "ing_old_123",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": None,
        }
        store.get_job.return_value = original
        store.find_active_retry = MagicMock(return_value=None)

        result = svc.retry_job("ing_old_123")
        assert isinstance(result, JobResult)
        assert result.ingestion_job_id != "ing_old_123"
        assert result.original_job_id == "ing_old_123"
        assert result.retry_of_job_id == "ing_old_123"

        # New job should have source="retry"
        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["source"] == "retry"
        assert call_kwargs["job_type"] == "dcp_current_plan"
        assert call_kwargs["params"] == {"domain": "basic"}
        assert call_kwargs["retry_of_job_id"] == "ing_old_123"
        assert call_kwargs["parent_job_id"] is None

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
        store.find_active_retry = MagicMock(return_value=None)
        result = svc.retry_job("ing_partial_1")
        assert result.original_job_id == "ing_partial_1"
        assert result.retry_of_job_id == "ing_partial_1"

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
        store.find_active_retry = MagicMock(return_value=None)
        result = svc.retry_job("ing_cancel_1")
        assert result.original_job_id == "ing_cancel_1"

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
    """P2: retry_job writes retry_of_job_id and rejects active retries."""

    def test_retry_writes_retry_of_job_id(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_orig_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": "ing_parent_1",
        }
        store.get_job.return_value = original
        store.find_active_retry = MagicMock(return_value=None)

        result = svc.retry_job("ing_orig_1")
        assert result.retry_of_job_id == "ing_orig_1"
        assert result.original_job_id == "ing_orig_1"

        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["retry_of_job_id"] == "ing_orig_1"
        assert call_kwargs["parent_job_id"] == "ing_parent_1"

    def test_retry_already_running_rejected(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_orig_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({}),
            "status": "failed",
            "parent_job_id": None,
        }
        store.get_job.return_value = original
        store.find_active_retry = MagicMock(return_value={
            "ingestion_job_id": "ing_retry_active",
            "status": "accepted",
        })

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_job("ing_orig_1")
        assert exc_info.value.error_code == "retry_already_running"

    def test_retry_child_preserves_parent_job_id(self):
        """Fanout child retry should preserve parent_job_id from original."""
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_child_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({"domain": "basic"}),
            "status": "failed",
            "parent_job_id": "ing_parent_fanout",
        }
        store.get_job.return_value = original
        store.find_active_retry = MagicMock(return_value=None)

        result = svc.retry_job("ing_child_1")
        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["parent_job_id"] == "ing_parent_fanout"
        assert call_kwargs["retry_of_job_id"] == "ing_child_1"


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
            "ing_child_0": {"ingestion_job_id": "ing_child_0", "status": "failed"},
            "ing_child_1": {"ingestion_job_id": "ing_child_1", "status": "cancelled"},
        }.get(jid))
        store.find_active_retry = MagicMock(return_value=None)
        store.update_fanout_item_for_retry = MagicMock()
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

    def test_failed_items_submit_new_child_jobs(self):
        svc, store, _ = self._make_fanout_setup()

        result = svc.retry_failed_children("ing_parent_1")
        assert result["submitted"] == 2
        assert result["skipped"] == 0
        assert len(result["items"]) == 2

        # Check first item
        item0 = result["items"][0]
        assert item0["old_child_job_id"] == "ing_child_0"
        assert item0["new_child_job_id"].startswith("ing_dcp_current_plan_")
        assert item0["status"] == "submitted"

    def test_new_child_has_parent_and_retry_of(self):
        svc, store, _ = self._make_fanout_setup()
        svc.retry_failed_children("ing_parent_1")

        # Check create_ingestion_job calls
        calls = store.create_ingestion_job.call_args_list
        assert len(calls) == 2
        for call in calls:
            kwargs = call[1]
            assert kwargs["parent_job_id"] == "ing_parent_1"
            assert kwargs["source"] == "retry"

        # First call should have retry_of_job_id = ing_child_0
        assert calls[0][1]["retry_of_job_id"] == "ing_child_0"
        assert calls[1][1]["retry_of_job_id"] == "ing_child_1"

    def test_fanout_item_updated_with_new_child(self):
        svc, store, _ = self._make_fanout_setup()
        result = svc.retry_failed_children("ing_parent_1")

        # update_fanout_item_for_retry should be called for each item
        assert store.update_fanout_item_for_retry.call_count == 2

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
        store.find_active_retry = MagicMock(return_value=None)
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

    def test_active_retry_skips_all_raises_no_retry_submitted(self):
        """All items skipped due to active retry → no_retry_submitted, no reopen."""
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
        store.get_job = MagicMock(return_value={"ingestion_job_id": "ing_child_0", "status": "failed"})
        store.find_active_retry = MagicMock(return_value={"ingestion_job_id": "ing_retry_active", "status": "accepted"})
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_parent_1")
        assert exc_info.value.error_code == "no_retry_submitted"
        store.reopen_fanout_run.assert_not_called()
        store.reopen_parent_ingestion_job.assert_not_called()

    def test_submit_command_fails_raises_no_retry_submitted(self):
        """submit_command raises JobServiceError → no_retry_submitted, no reopen."""
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
        store.get_job = MagicMock(return_value={"ingestion_job_id": "ing_child_0", "status": "failed"})
        store.find_active_retry = MagicMock(return_value=None)
        store.reopen_fanout_run = MagicMock()
        store.reopen_parent_ingestion_job = MagicMock()
        # Make submit_command fail by removing the connector
        svc._trigger_clients = {}

        with pytest.raises(JobServiceError) as exc_info:
            svc.retry_failed_children("ing_parent_1")
        assert exc_info.value.error_code == "no_retry_submitted"
        store.reopen_fanout_run.assert_not_called()
        store.reopen_parent_ingestion_job.assert_not_called()

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
        store.find_active_retry = MagicMock(return_value=None)
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

    def test_retry_returns_retry_of_job_id(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_job.return_value = JobResult(
            ingestion_job_id="ing_new_retry",
            status="accepted",
            original_job_id="ing_old_1",
            retry_of_job_id="ing_old_1",
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_old_1/retry")
        assert resp.status_code == 202
        data = resp.json()
        assert data["ingestion_job_id"] == "ing_new_retry"
        assert data["original_job_id"] == "ing_old_1"
        assert data["retry_of_job_id"] == "ing_old_1"

    def test_retry_already_running_returns_409(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_job.side_effect = JobServiceError(
            "retry_already_running", "active retry exists"
        )

        tc = self._build_client(mock_job_svc)
        resp = tc.post("/ingestion/v1/jobs/ing_old_1/retry")
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "retry_already_running"

    def test_retry_failed_children_returns_submitted(self):
        mock_job_svc = MagicMock(spec=JobService)
        mock_job_svc.retry_failed_children.return_value = {
            "parent_job_id": "ing_parent_1",
            "submitted": 2,
            "skipped": 0,
            "items": [
                {"item_index": 0, "old_child_job_id": "ing_c0", "new_child_job_id": "ing_c0_new", "status": "submitted"},
                {"item_index": 1, "old_child_job_id": "ing_c1", "new_child_job_id": "ing_c1_new", "status": "submitted"},
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
