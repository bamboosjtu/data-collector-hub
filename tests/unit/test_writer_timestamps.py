"""Tests for business table ingestion meta timestamps."""
from __future__ import annotations

import sqlite3
from unittest.mock import patch

from src.datahub.core.specs import ColumnSpec, TableSpec
from src.datahub.core.time_utils import datahub_now_text
from src.datahub.storage.ddl import create_business_table, INGEST_META_COLUMNS
from src.datahub.storage.writer import write_table


def _make_table() -> TableSpec:
    return TableSpec(
        table_name="test_table",
        dataset_key="test",
        description="test table",
        columns={
            "id": ColumnSpec(name="id", type="text", nullable=False),
            "name": ColumnSpec(name="name", type="text", nullable=True),
        },
        primary_key=("id",),
        write_mode="upsert",
        scope_column_names=(),
    )


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    table = _make_table()
    create_business_table(conn, table)
    return conn


PAYLOAD = {
    "message_id": "msg_001",
    "downloader_job_id": "dl_001",
    "collect_run_id": "run_001",
    "payload_hash": "abc123",
}


class TestIngestMetaTimestamps:
    def test_insert_has_created_at(self):
        """New business row should have _ingest_created_at populated."""
        table = _make_table()
        conn = _make_conn()

        rows = [{"id": "1", "name": "alpha"}]
        write_table(conn, table, rows, {}, PAYLOAD, "job_001")

        row = dict(conn.execute("SELECT * FROM test_table WHERE id = '1'").fetchone())
        assert row["_ingest_created_at"] is not None
        assert len(row["_ingest_created_at"]) == 19  # "YYYY-MM-DD HH:MM:SS"

    def test_insert_has_updated_at(self):
        """New business row should have _ingest_updated_at populated."""
        table = _make_table()
        conn = _make_conn()

        rows = [{"id": "1", "name": "alpha"}]
        write_table(conn, table, rows, {}, PAYLOAD, "job_001")

        row = dict(conn.execute("SELECT * FROM test_table WHERE id = '1'").fetchone())
        assert row["_ingest_updated_at"] is not None
        assert len(row["_ingest_updated_at"]) == 19

    def test_upsert_preserves_created_at(self):
        """Upsert should NOT overwrite _ingest_created_at."""
        table = _make_table()
        conn = _make_conn()

        # First insert
        rows = [{"id": "1", "name": "alpha"}]
        write_table(conn, table, rows, {}, PAYLOAD, "job_001")
        original_created = dict(conn.execute("SELECT * FROM test_table WHERE id = '1'").fetchone())["_ingest_created_at"]

        # Upsert update with different timestamp
        with patch("src.datahub.storage.writer.datahub_now_text", return_value="2099-12-31 23:59:59"):
            rows2 = [{"id": "1", "name": "beta"}]
            write_table(conn, table, rows2, {}, PAYLOAD, "job_002")

        row = dict(conn.execute("SELECT * FROM test_table WHERE id = '1'").fetchone())
        assert row["_ingest_created_at"] == original_created  # preserved
        assert row["name"] == "beta"  # updated
        assert row["_ingest_updated_at"] == "2099-12-31 23:59:59"  # updated

    def test_upsert_updates_updated_at(self):
        """Upsert should update _ingest_updated_at to current time."""
        table = _make_table()
        conn = _make_conn()

        # First insert
        rows = [{"id": "1", "name": "alpha"}]
        write_table(conn, table, rows, {}, PAYLOAD, "job_001")
        first_updated = dict(conn.execute("SELECT * FROM test_table WHERE id = '1'").fetchone())["_ingest_updated_at"]

        # Upsert update with different timestamp
        with patch("src.datahub.storage.writer.datahub_now_text", return_value="2099-12-31 23:59:59"):
            rows2 = [{"id": "1", "name": "beta"}]
            write_table(conn, table, rows2, {}, PAYLOAD, "job_002")

        row = dict(conn.execute("SELECT * FROM test_table WHERE id = '1'").fetchone())
        assert row["_ingest_updated_at"] == "2099-12-31 23:59:59"  # updated
