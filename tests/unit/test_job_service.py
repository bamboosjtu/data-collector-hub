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
        }
        store.get_job.return_value = original

        result = svc.retry_job("ing_old_123")
        assert isinstance(result, JobResult)
        assert result.ingestion_job_id != "ing_old_123"
        assert result.original_job_id == "ing_old_123"

        # New job should have source="retry"
        call_kwargs = store.create_ingestion_job.call_args[1]
        assert call_kwargs["source"] == "retry"
        assert call_kwargs["job_type"] == "dcp_current_plan"
        assert call_kwargs["params"] == {"domain": "basic"}

    def test_retry_partial_job_succeeds(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_partial_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({}),
            "status": "partial",
        }
        store.get_job.return_value = original
        result = svc.retry_job("ing_partial_1")
        assert result.original_job_id == "ing_partial_1"

    def test_retry_cancelled_job_succeeds(self):
        svc, store, _ = _make_job_service()
        original = {
            "ingestion_job_id": "ing_cancel_1",
            "trigger_key": "dcp_current_plan",
            "params_json": json.dumps({}),
            "status": "cancelled",
        }
        store.get_job.return_value = original
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
