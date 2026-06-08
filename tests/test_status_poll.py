"""Tests for downloader job status polling and parent job aggregation."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.datahub.core.registry import SchemaRegistry, TableSpec, ColumnSpec
from src.datahub.core.trigger_runtime import (
    ExternalSyncClient,
    poll_downloader_jobs,
    _extract_producer_result,
    _aggregate_parent_jobs,
    _DOWNLOADER_STATUS_MAP,
    _TERMINAL_STATUSES,
)
from src.datahub.storage.ddl import create_metadata_tables
from src.datahub.storage.sqlite import DataHubStore

# Use project-local temp dir to avoid Windows permission issues with system temp
_TMP_BASE = Path(__file__).resolve().parents[1] / ".tmp_test"


def _make_registry() -> SchemaRegistry:
    """Create a minimal registry for testing."""
    tables = {
        "test_table": TableSpec(
            table_name="test_table",
            dataset_key="test_dataset",
            description="test",
            write_mode="upsert",
            primary_key=("id",),
            scope_column_names=("scope_col",),
            columns={
                "id": ColumnSpec(name="id", type="string", nullable=False),
                "scope_col": ColumnSpec(name="scope_col", type="string", nullable=False),
            },
        ),
    }
    return SchemaRegistry(
        version=1,
        tables=tables,
        datasets={"test_dataset"},
        raw={"version": 1, "tables": {"test_table": {}}},
    )


def _make_store(test_name: str) -> DataHubStore:
    registry = _make_registry()
    db_dir = _TMP_BASE / test_name
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "test.db"
    # Remove existing db to start fresh
    if db_path.exists():
        db_path.unlink()
    store = DataHubStore(db_path, registry)
    store.init_schema(dev_mode=True)
    return store


def _insert_job(conn: sqlite3.Connection, *, job_id: str, producer_job_id: str, status: str = "accepted", plugin_id: str = "dcp", parent_job_id: str | None = None) -> None:
    conn.execute(
        """INSERT INTO ingestion_jobs(ingestion_job_id, parent_job_id, plugin_id, trigger_key, downloader_job_id, dataset_key, params_json, status, started_at)
        VALUES (?, ?, ?, 'test_cmd', ?, 'test_dataset', '{}', ?, CURRENT_TIMESTAMP)""",
        (job_id, parent_job_id, plugin_id, producer_job_id, status),
    )


class TestExtractProducerResult:
    def test_extracts_all_fields(self):
        dl_status = {
            "status": "succeeded",
            "collect_total": 5,
            "collect_done": 5,
            "collect_failed": 0,
            "row_count": 416,
            "message_count": 1,
            "outbox_delivered": 1,
            "outbox_failed": 0,
            "current_message": "done",
        }
        result = _extract_producer_result(dl_status)
        assert result["collect_total"] == 5
        assert result["row_count"] == 416
        assert result["outbox_delivered"] == 1

    def test_missing_fields_default_to_none(self):
        result = _extract_producer_result({"status": "running"})
        assert result["collect_total"] is None
        assert result["row_count"] is None


class TestPollDownloaderJobs:
    def test_accepted_to_failed_syncs(self):
        """downloader returns failed -> Hub job becomes failed."""
        store = _make_store("poll_failed")
        with store.connect() as conn:
            _insert_job(conn, job_id="job_1", producer_job_id="dl_1", status="accepted")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {
            "status": "failed",
            "current_message": "stalled: no collect task completed",
            "collect_total": 1,
            "collect_failed": 1,
        }

        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["polled"] == 1
        assert summary["updated"] == 1
        assert summary["failed"] == 1

        job = store.get_job("job_1")
        assert job["status"] == "failed"
        assert "stalled" in (job["error"] or "")

    def test_accepted_to_succeeded_syncs(self):
        """downloader returns succeeded -> Hub job becomes succeeded."""
        store = _make_store("poll_succeeded")
        with store.connect() as conn:
            _insert_job(conn, job_id="job_2", producer_job_id="dl_2", status="accepted")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {
            "status": "succeeded",
            "collect_total": 1,
            "collect_done": 1,
            "row_count": 416,
        }

        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["updated"] == 1

        job = store.get_job("job_2")
        assert job["status"] == "succeeded"
        result = json.loads(job["result_json"])
        assert result["row_count"] == 416

    def test_accepted_to_partial_syncs(self):
        """downloader returns partial -> Hub job becomes partial."""
        store = _make_store("poll_partial")
        with store.connect() as conn:
            _insert_job(conn, job_id="job_3", producer_job_id="dl_3", status="accepted")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {
            "status": "partial",
            "current_message": "some tasks failed",
            "collect_total": 5,
            "collect_done": 3,
            "collect_failed": 2,
        }

        summary = poll_downloader_jobs(store, {"dcp": client})
        job = store.get_job("job_3")
        assert job["status"] == "partial"

    def test_terminal_jobs_not_polled(self):
        """Already terminal jobs should not be polled."""
        store = _make_store("poll_terminal")
        with store.connect() as conn:
            _insert_job(conn, job_id="job_4", producer_job_id="dl_4", status="succeeded")

        client = MagicMock(spec=ExternalSyncClient)
        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["polled"] == 0
        client.get_job_status.assert_not_called()

    def test_stale_job_marked_failed(self):
        """Jobs non-terminal for too long get marked failed."""
        store = _make_store("poll_stale")
        with store.connect() as conn:
            _insert_job(conn, job_id="job_5", producer_job_id="dl_5", status="accepted")
            # Manually set started_at to 31 minutes ago
            conn.execute("UPDATE ingestion_jobs SET started_at = datetime('now', '-1860 seconds') WHERE ingestion_job_id = 'job_5'")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {"status": "running"}

        summary = poll_downloader_jobs(store, {"dcp": client}, stale_threshold_seconds=1800)
        assert summary["stale"] == 1

        job = store.get_job("job_5")
        assert job["status"] == "failed"
        assert "stale" in (job["error"] or "")

    def test_downloader_unreachable_skips(self):
        """If downloader is unreachable, skip without error."""
        store = _make_store("poll_unreachable")
        with store.connect() as conn:
            _insert_job(conn, job_id="job_6", producer_job_id="dl_6", status="accepted")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = None  # unreachable

        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["polled"] == 0
        job = store.get_job("job_6")
        assert job["status"] == "accepted"  # unchanged

    def test_fan_out_parent_not_stale(self):
        """Fan-out parent jobs (with children) should NOT be marked stale.
        Their terminal state is determined solely by _aggregate_parent_jobs."""
        store = _make_store("poll_parent_not_stale")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_stale", producer_job_id="dl_ps", status="running")
            _insert_job(conn, job_id="child_stale", producer_job_id="dl_cs", status="running", parent_job_id="parent_stale")
            # Set parent started_at to 31 minutes ago
            conn.execute("UPDATE ingestion_jobs SET started_at = datetime('now', '-1860 seconds') WHERE ingestion_job_id = 'parent_stale'")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {"status": "running"}

        summary = poll_downloader_jobs(store, {"dcp": client}, stale_threshold_seconds=1800)
        assert summary["stale"] == 0

        parent = store.get_job("parent_stale")
        assert parent["status"] == "running"  # NOT marked stale

    def test_standalone_job_still_stale(self):
        """Standalone jobs (no children) should still be marked stale."""
        store = _make_store("poll_standalone_stale")
        with store.connect() as conn:
            _insert_job(conn, job_id="standalone_stale", producer_job_id="dl_ss", status="running")
            conn.execute("UPDATE ingestion_jobs SET started_at = datetime('now', '-1860 seconds') WHERE ingestion_job_id = 'standalone_stale'")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {"status": "running"}

        summary = poll_downloader_jobs(store, {"dcp": client}, stale_threshold_seconds=1800)
        assert summary["stale"] == 1

        job = store.get_job("standalone_stale")
        assert job["status"] == "failed"
        assert "stale" in (job["error"] or "")

    def test_fan_out_parent_not_polled(self):
        """Fan-out parent jobs (with children) should NOT be polled via downloader /sync/jobs/{id}.
        They are not real downloader jobs — polling them produces 404."""
        store = _make_store("poll_parent_not_polled")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_poll", producer_job_id="dl_pp", status="running")
            _insert_job(conn, job_id="child_poll", producer_job_id="dl_cp", status="running", parent_job_id="parent_poll")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {"status": "running"}

        summary = poll_downloader_jobs(store, {"dcp": client})
        # Parent should NOT be polled — only child should be
        assert summary["polled"] == 1  # only the child
        # Verify parent was not polled by checking call args
        called_ids = [call.args[0] for call in client.get_job_status.call_args_list]
        assert "dl_pp" not in called_ids  # parent's downloader_job_id not called
        assert "dl_cp" in called_ids  # child's downloader_job_id called

    def test_fan_out_child_is_polled(self):
        """Fan-out child jobs should still be polled normally."""
        store = _make_store("poll_child_polled")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_cp", producer_job_id="dl_pcp", status="running")
            _insert_job(conn, job_id="child_cp", producer_job_id="dl_ccp", status="running", parent_job_id="parent_cp")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {"status": "succeeded", "collect_total": 1, "collect_done": 1, "row_count": 10}

        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["polled"] == 1
        assert summary["updated"] == 1

        child = store.get_job("child_cp")
        assert child["status"] == "succeeded"

    def test_standalone_job_is_polled(self):
        """Standalone downloader_sync jobs (no children) should still be polled."""
        store = _make_store("poll_standalone_polled")
        with store.connect() as conn:
            _insert_job(conn, job_id="standalone_poll", producer_job_id="dl_sp", status="accepted")

        client = MagicMock(spec=ExternalSyncClient)
        client.get_job_status.return_value = {"status": "succeeded", "collect_total": 1, "collect_done": 1, "row_count": 100}

        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["polled"] == 1
        assert summary["updated"] == 1

        job = store.get_job("standalone_poll")
        assert job["status"] == "succeeded"

    def test_parent_aggregation_after_child_polling(self):
        """Parent status should be aggregated by _aggregate_parent_jobs after child polling."""
        store = _make_store("poll_agg_after_child")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_agg", producer_job_id="dl_pagg", status="running")
            _insert_job(conn, job_id="child_agg_a", producer_job_id="dl_cagga", status="running", parent_job_id="parent_agg")
            _insert_job(conn, job_id="child_agg_b", producer_job_id="dl_caggb", status="succeeded", parent_job_id="parent_agg")

        client = MagicMock(spec=ExternalSyncClient)

        def mock_status(dl_job_id):
            if dl_job_id == "dl_cagga":
                return {"status": "succeeded", "collect_total": 1, "collect_done": 1, "row_count": 5}
            return None

        client.get_job_status.side_effect = mock_status

        summary = poll_downloader_jobs(store, {"dcp": client})
        assert summary["polled"] == 1

        # After polling, child_agg_a should be succeeded, and parent should be aggregated
        parent = store.get_job("parent_agg")
        assert parent["status"] == "succeeded"


class TestAggregateParentJobs:
    def test_all_children_succeeded_parent_succeeded(self):
        """All children succeeded -> parent succeeded."""
        store = _make_store("agg_succeeded")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_1", producer_job_id="dl_p1", status="running")
            _insert_job(conn, job_id="child_1a", producer_job_id="dl_c1a", status="succeeded", parent_job_id="parent_1")
            _insert_job(conn, job_id="child_1b", producer_job_id="dl_c1b", status="succeeded", parent_job_id="parent_1")

        _aggregate_parent_jobs(store)
        parent = store.get_job("parent_1")
        assert parent["status"] == "succeeded"

    def test_mixed_children_parent_partial(self):
        """Some children failed, some succeeded -> parent partial."""
        store = _make_store("agg_partial")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_2", producer_job_id="dl_p2", status="running")
            _insert_job(conn, job_id="child_2a", producer_job_id="dl_c2a", status="succeeded", parent_job_id="parent_2")
            _insert_job(conn, job_id="child_2b", producer_job_id="dl_c2b", status="failed", parent_job_id="parent_2", )
            # Need to set error for failed child
            conn.execute("UPDATE ingestion_jobs SET error = 'timeout' WHERE ingestion_job_id = 'child_2b'")

        _aggregate_parent_jobs(store)
        parent = store.get_job("parent_2")
        assert parent["status"] == "partial"

    def test_all_children_failed_parent_failed(self):
        """All children failed -> parent failed."""
        store = _make_store("agg_failed")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_3", producer_job_id="dl_p3", status="running")
            _insert_job(conn, job_id="child_3a", producer_job_id="dl_c3a", status="failed", parent_job_id="parent_3")
            conn.execute("UPDATE ingestion_jobs SET error = 'err1' WHERE ingestion_job_id = 'child_3a'")

        _aggregate_parent_jobs(store)
        parent = store.get_job("parent_3")
        assert parent["status"] == "failed"

    def test_non_terminal_children_parent_stays_running(self):
        """Not all children terminal -> parent stays running."""
        store = _make_store("agg_running")
        with store.connect() as conn:
            _insert_job(conn, job_id="parent_4", producer_job_id="dl_p4", status="running")
            _insert_job(conn, job_id="child_4a", producer_job_id="dl_c4a", status="succeeded", parent_job_id="parent_4")
            _insert_job(conn, job_id="child_4b", producer_job_id="dl_c4b", status="running", parent_job_id="parent_4")

        _aggregate_parent_jobs(store)
        parent = store.get_job("parent_4")
        assert parent["status"] == "running"  # unchanged
