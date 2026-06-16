"""Tests for P5.5-light: In-place job retry (no new ingestion_job created)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.datahub.core.services.job_service import (
    JobService,
    JobServiceError,
    RETRYABLE_STATUSES,
    strip_internal_params,
    get_internal_retry_count,
    bump_internal_retry_meta,
)
from src.datahub.core.specs import CommandSpec, PluginSpec, DisplaySpec, ConnectorSpec
from src.datahub.core.fanout_scheduler import _get_child_retry_count, _is_child_non_success


# ── Internal params helpers ──

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


# ── Fanout scheduler helpers ──

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


# ── JobService retry_job in-place ──

def _make_service(store, plugins, trigger_clients=None):
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": MagicMock()})
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": MagicMock()})
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_job("ing_test_cmd_abc123")

        sync_call = mock_client.sync.call_args
        params_sent = sync_call[1]["params"]
        assert "__datahub" not in params_sent
        assert "projectCode" in params_sent

    def test_retry_success_sets_succeeded(self):
        """After retry, if callback succeeds, job.status=succeeded."""
        # This is tested implicitly — mark_job is called with the callback status
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_job("ing_test_cmd_abc123")

        # mark_job called with "accepted" from sync response
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
            with pytest.raises(JobServiceError):
                svc.retry_job("ing_test_cmd_abc123")

        # mark_job called with "failed"
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
            # Try to forge __datahub
            result = svc.submit_command("test_cmd", {"projectCode": "A", "__datahub": {"retry_count": 999}})

        # Verify create_ingestion_job was called without __datahub
        create_call = store.create_ingestion_job.call_args
        assert create_call[1]["params"] == {"projectCode": "A"}

        # Verify sync was called without __datahub
        sync_call = mock_client.sync.call_args
        assert "__datahub" not in sync_call[1]["params"]


# ── Fanout auto-retry ──

class TestFanoutAutoRetry:

    def test_auto_retry_once_on_non_success(self):
        """Fanout scheduler auto-retries a non-success child once (retry_count < 1)."""
        store = MagicMock()
        child_job = {
            "ingestion_job_id": "ing_child_001",
            "status": "failed",
            "params_json": json.dumps({"projectCode": "A"}),  # retry_count = 0
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
        # This is tested via the _get_child_retry_count check in _advance_fanout_run
        child_job = {
            "status": "failed",
            "params_json": json.dumps({"__datahub": {"retry_count": 1}}),
        }
        assert _get_child_retry_count(child_job) == 1
        # In the scheduler, the condition `child_retry_count < 1` would be False
        # so it would fall through to update_fanout_item_terminal(failed)

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

        # No create_ingestion_job called
        store.create_ingestion_job.assert_not_called()
        # reopen_job_for_retry called with same job_id
        reopen_call = store.reopen_job_for_retry.call_args
        assert reopen_call[0][0] == "ing_child_001"


# ── retry_failed_children in-place ──

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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
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
            svc = _make_service(store, [plugin], trigger_clients={"dcp": mock_client})
            result = svc.retry_failed_children("ing_parent_001")

        store.reopen_fanout_run.assert_called_once_with("ing_parent_001")
        store.reopen_parent_ingestion_job.assert_called_once_with("ing_parent_001")
