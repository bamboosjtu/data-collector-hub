"""Tests for P5.3: Project domain snapshot tables use replace_scope with scoped delete."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.datahub.ingestion.validator import validate_payload
from src.datahub.storage.sqlite import DataHubStore
from src.datahub.storage.writer import write_table


# ── Helpers ──

def _noop_scope_mappings(table_name: str, scope_values: dict) -> dict:
    return scope_values


def _make_store():
    from src.datahub.core.plugin_loader import load_all_plugins
    from src.datahub.core.registry import load_registry_from_plugins
    from src.datahub.settings import Settings
    d = tempfile.mkdtemp()
    db_path = str(Path(d) / "test_writer_replace_scope.db")
    plugins = load_all_plugins(Settings.plugin_dir)
    registry = load_registry_from_plugins(plugins)
    s = DataHubStore(db_path, registry)
    s.init_schema(dev_mode=True)
    return s


def _make_payload(table_name, dataset_key, scope_values, rows,
                  message_id="msg_test", idempotency_key="idem_test",
                  downloader_job_id="dl_test", collect_run_id="run_test",
                  payload_hash="hash_test"):
    return {
        "message_id": message_id,
        "idempotency_key": idempotency_key,
        "downloader_job_id": downloader_job_id,
        "collect_run_id": collect_run_id,
        "payload_hash": payload_hash,
        "dataset_key": dataset_key,
        "tables": [{
            "table_name": table_name,
            "scope_values": scope_values,
            "rows": rows,
        }],
    }


# ── Case 1: tower replace_scope deletes old rows ──

class TestTowerReplaceScope:

    def test_replace_scope_deletes_old_rows(self):
        """New batch with fewer rows should delete stale rows in the same scope."""
        store = _make_store()

        # Insert initial data: singleProjectCode=A, id=1 and id=2
        with store.connect() as conn:
            conn.execute(
                "INSERT INTO dcp_project_tower (singleProjectCode, id) VALUES (?, ?)",
                ("A", "1"),
            )
            conn.execute(
                "INSERT INTO dcp_project_tower (singleProjectCode, id) VALUES (?, ?)",
                ("A", "2"),
            )
            # Also insert a different scope to verify it's not deleted
            conn.execute(
                "INSERT INTO dcp_project_tower (singleProjectCode, id) VALUES (?, ?)",
                ("B", "10"),
            )

        # New batch: only id=1 for scope A
        payload = _make_payload(
            "dcp_project_tower", "tower",
            {"singleProjectCode": "A"},
            [{"singleProjectCode": "A", "id": "1"}],
        )

        validated, skipped = validate_payload(store.registry, payload, store.apply_scope_mappings)
        assert len(validated) == 1
        table, scope_values, rows = validated[0]
        assert table.table_name == "dcp_project_tower"
        assert scope_values["singleProjectCode"] == "A"
        assert len(rows) == 1

        with store.connect() as conn:
            stats = write_table(conn, table, rows, scope_values, payload, None)

        assert stats["deleted_count"] == 2  # Deleted both old rows in scope A
        assert stats["row_count"] == 1

        # Verify: scope A has only id=1, scope B untouched
        with store.connect() as conn:
            a_rows = conn.execute("SELECT id FROM dcp_project_tower WHERE singleProjectCode='A' ORDER BY id").fetchall()
            b_rows = conn.execute("SELECT id FROM dcp_project_tower WHERE singleProjectCode='B'").fetchall()
        assert [r[0] for r in a_rows] == ["1"]
        assert len(b_rows) == 1  # B untouched


# ── Case 2: tower empty snapshot deletes old rows ──

class TestTowerEmptySnapshot:

    def test_empty_snapshot_deletes_old_rows(self):
        """Empty rows=[] for replace_scope should still delete old rows in scope."""
        store = _make_store()

        # Insert initial data
        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_project_tower (singleProjectCode, id) VALUES (?, ?)", ("A", "1"))
            conn.execute("INSERT INTO dcp_project_tower (singleProjectCode, id) VALUES (?, ?)", ("A", "2"))

        # Empty snapshot for scope A
        payload = _make_payload(
            "dcp_project_tower", "tower",
            {"singleProjectCode": "A"},
            [],  # empty rows
        )

        validated, skipped = validate_payload(store.registry, payload, store.apply_scope_mappings)
        assert len(validated) == 1
        table, scope_values, rows = validated[0]
        assert rows == []  # empty but still validated

        with store.connect() as conn:
            stats = write_table(conn, table, rows, scope_values, payload, None)

        assert stats["deleted_count"] == 2
        assert stats["row_count"] == 0

        # Verify: scope A has 0 rows
        with store.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM dcp_project_tower WHERE singleProjectCode='A'").fetchone()[0]
        assert count == 0


# ── Case 3: substation replace_scope ──

class TestSubstationReplaceScope:

    def test_replace_scope_replaces_old_data(self):
        """Substation with replace_scope should replace old data in scope."""
        store = _make_store()

        # Insert initial substation
        with store.connect() as conn:
            conn.execute(
                "INSERT INTO dcp_project_substation (singleProjectCode, longitude, latitude) VALUES (?, ?, ?)",
                ("SP001", "116.4", "39.9"),
            )

        # New batch with updated coordinates
        payload = _make_payload(
            "dcp_project_substation", "substation",
            {"singleProjectCode": "SP001"},
            [{"singleProjectCode": "SP001", "longitude": "117.0", "latitude": "40.0"}],
        )

        validated, _ = validate_payload(store.registry, payload, store.apply_scope_mappings)
        table, scope_values, rows = validated[0]

        with store.connect() as conn:
            write_table(conn, table, rows, scope_values, payload, None)

        # Verify: old values replaced
        with store.connect() as conn:
            row = conn.execute("SELECT longitude, latitude FROM dcp_project_substation WHERE singleProjectCode='SP001'").fetchone()
        assert row[0] == "117.0"
        assert row[1] == "40.0"


# ── Case 4: line_branches + line_sections replace_scope ──

class TestLineBranchesSectionsReplaceScope:

    def test_line_branches_replace_scope(self):
        """Line branches with replace_scope should delete stale branches."""
        store = _make_store()

        # Insert initial branches for biddingSectionCode=B
        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_project_line_branches (biddingSectionCode, branchId, branchName) VALUES (?, ?, ?)",
                         ("B", "br1", "Branch 1"))
            conn.execute("INSERT INTO dcp_project_line_branches (biddingSectionCode, branchId, branchName) VALUES (?, ?, ?)",
                         ("B", "br2", "Branch 2"))
            conn.execute("INSERT INTO dcp_project_line_branches (biddingSectionCode, branchId, branchName) VALUES (?, ?, ?)",
                         ("C", "br3", "Branch 3"))

        # New batch: only br1 for scope B
        payload = _make_payload(
            "dcp_project_line_branches", "line_section",
            {"biddingSectionCode": "B"},
            [{"biddingSectionCode": "B", "branchId": "br1", "branchName": "Branch 1 updated"}],
        )

        validated, _ = validate_payload(store.registry, payload, store.apply_scope_mappings)
        table, scope_values, rows = validated[0]

        with store.connect() as conn:
            write_table(conn, table, rows, scope_values, payload, None)

        # Verify: B has only br1, C untouched
        with store.connect() as conn:
            b_rows = conn.execute("SELECT branchId FROM dcp_project_line_branches WHERE biddingSectionCode='B' ORDER BY branchId").fetchall()
            c_rows = conn.execute("SELECT branchId FROM dcp_project_line_branches WHERE biddingSectionCode='C'").fetchall()
        assert [r[0] for r in b_rows] == ["br1"]
        assert len(c_rows) == 1

    def test_line_sections_replace_scope(self):
        """Line sections with replace_scope should delete stale sections."""
        store = _make_store()

        with store.connect() as conn:
            conn.execute("INSERT INTO dcp_project_line_sections (biddingSectionCode, sectionId, sectionNo) VALUES (?, ?, ?)",
                         ("B", "s1", "1"))
            conn.execute("INSERT INTO dcp_project_line_sections (biddingSectionCode, sectionId, sectionNo) VALUES (?, ?, ?)",
                         ("B", "s2", "2"))

        # New batch: only s1
        payload = _make_payload(
            "dcp_project_line_sections", "line_section",
            {"biddingSectionCode": "B"},
            [{"biddingSectionCode": "B", "sectionId": "s1", "sectionNo": "1"}],
        )

        validated, _ = validate_payload(store.registry, payload, store.apply_scope_mappings)
        table, scope_values, rows = validated[0]

        with store.connect() as conn:
            write_table(conn, table, rows, scope_values, payload, None)

        with store.connect() as conn:
            b_rows = conn.execute("SELECT sectionId FROM dcp_project_line_sections WHERE biddingSectionCode='B' ORDER BY sectionId").fetchall()
        assert [r[0] for r in b_rows] == ["s1"]
