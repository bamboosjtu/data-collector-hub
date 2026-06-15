"""Tests for P4 MVP release hardening.

Covers:
1. /health/ready endpoint (DB check, no secrets, scheduler status)
2. backup_sqlite.py script (backup temp DB)
3. mvp_check_env.py (missing required env fails)
4. mvp_smoke_check.py (SQLite table check on temp DB, no ALTER TABLE check)
5. Schema baseline: no ALTER TABLE in ddl.py
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from src.datahub.api.health import build_health_router
from src.datahub.core.plugin_loader import load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.settings import Settings
from src.datahub.storage.ddl import create_metadata_tables
from src.datahub.storage.sqlite import DataHubStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_store_with_db():
    """Create a temp-file-based store with schema initialized."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test.db"
    plugins = load_all_plugins(Settings.plugin_dir)
    registry = load_registry_from_plugins(plugins)
    store = DataHubStore(db_path, registry)
    store.init_schema(dev_mode=True)
    return store, db_path, registry


# ---------------------------------------------------------------------------
# 1. /health/ready
# ---------------------------------------------------------------------------

class TestHealthReady:
    """Test /health/ready endpoint."""

    def test_ready_ok(self):
        store, db_path, registry = _make_store_with_db()
        settings = Settings(db_path=db_path, dev_mode=True)
        router = build_health_router(registry, store=store, settings=settings)

        from fastapi import FastAPI
        app = FastAPI()
        app.state.fanout_scheduler_stop = None
        app.include_router(router)

        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["db"] == "ok"
        assert "tables" in data
        assert data["scheduler_enabled"] is False
        assert data["daily_dcp_refresh_enabled"] is False
        assert data["fanout_scheduler"] == "unknown"
        assert "db_path" in data
        assert "api_key" not in data
        assert "callback_api_key" not in data

    def test_ready_scheduler_enabled(self):
        store, db_path, registry = _make_store_with_db()
        settings = Settings(
            db_path=db_path, dev_mode=True,
            collection_scheduler_enabled=True,
            daily_dcp_refresh_enabled=True,
        )
        router = build_health_router(registry, store=store, settings=settings)

        from fastapi import FastAPI
        app = FastAPI()
        app.state.fanout_scheduler_stop = None
        app.include_router(router)

        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/health/ready")
        data = resp.json()
        assert data["scheduler_enabled"] is True
        assert data["daily_dcp_refresh_enabled"] is True

    def test_ready_fanout_running(self):
        store, db_path, registry = _make_store_with_db()
        settings = Settings(db_path=db_path, dev_mode=True)
        router = build_health_router(registry, store=store, settings=settings)

        import threading
        stop_event = threading.Event()

        from fastapi import FastAPI
        app = FastAPI()
        app.state.fanout_scheduler_stop = stop_event
        app.include_router(router)

        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/health/ready")
        data = resp.json()
        assert data["fanout_scheduler"] == "running"

    def test_ready_no_secret_in_response(self):
        store, db_path, registry = _make_store_with_db()
        settings = Settings(db_path=db_path, dev_mode=True, callback_api_key="super-secret-key")
        router = build_health_router(registry, store=store, settings=settings)

        from fastapi import FastAPI
        app = FastAPI()
        app.state.fanout_scheduler_stop = None
        app.include_router(router)

        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/health/ready")
        body = resp.text
        assert "super-secret-key" not in body


# ---------------------------------------------------------------------------
# 2. backup_sqlite.py
# ---------------------------------------------------------------------------

class TestBackupSqlite:
    """Test backup_sqlite.py script."""

    def test_backup_temp_db(self):
        tmpdir = tempfile.mkdtemp()
        db_path = Path(tmpdir) / "test_backup.db"
        conn = sqlite3.connect(str(db_path))
        create_metadata_tables(conn)
        conn.execute(
            "INSERT INTO ingestion_jobs (ingestion_job_id, trigger_key, params_json, source, status) VALUES (?, ?, ?, ?, ?)",
            ("job-1", "test_cmd", "{}", "api", "succeeded"),
        )
        conn.commit()
        conn.close()

        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "backup_sqlite.py"), "--db", str(db_path)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"backup failed: {result.stderr}"
        backup_path = result.stdout.strip()
        assert backup_path, "no backup path printed"
        assert Path(backup_path).exists(), f"backup file not found: {backup_path}"
        assert Path(backup_path).stat().st_size > 0, "backup file is empty"

        conn2 = sqlite3.connect(backup_path)
        row = conn2.execute("SELECT ingestion_job_id FROM ingestion_jobs").fetchone()
        conn2.close()
        assert row is not None
        assert row[0] == "job-1"

    def test_backup_missing_db(self):
        tmpdir = tempfile.mkdtemp()
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "backup_sqlite.py"), "--db", str(Path(tmpdir) / "nonexistent.db")],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# 3. mvp_check_env.py
# ---------------------------------------------------------------------------

class TestMvpCheckEnv:
    """Test mvp_check_env.py script."""

    def test_prod_mode_missing_key_fails(self):
        env = os.environ.copy()
        env.pop("DATAHUB_CALLBACK_API_KEY", None)
        env["DATAHUB_DEV_MODE"] = "0"
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "mvp_check_env.py")],
            capture_output=True, text=True, env=env, cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0
        assert "FAIL" in result.stdout

    def test_dev_mode_missing_key_warns(self):
        env = os.environ.copy()
        env.pop("DATAHUB_CALLBACK_API_KEY", None)
        env["DATAHUB_DEV_MODE"] = "1"
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "mvp_check_env.py")],
            capture_output=True, text=True, env=env, cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0
        assert "WARN" in result.stdout


# ---------------------------------------------------------------------------
# 4. mvp_smoke_check.py - SQLite table check
# ---------------------------------------------------------------------------

class TestSmokeSqliteCheck:
    """Test smoke check's SQLite table verification on temp DB."""

    def test_check_sqlite_tables_on_valid_db(self):
        tmpdir = tempfile.mkdtemp()
        db_path = Path(tmpdir) / "test_smoke.db"
        conn = sqlite3.connect(str(db_path))
        create_metadata_tables(conn)
        conn.commit()
        conn.close()

        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from mvp_smoke_check import check_sqlite_tables

        ok, desc = check_sqlite_tables(str(db_path))
        assert ok, desc
        assert "all 6 required tables exist" in desc

    def test_check_sqlite_tables_missing_table(self):
        tmpdir = tempfile.mkdtemp()
        db_path = Path(tmpdir) / "test_incomplete.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE ingestion_jobs (id INTEGER)")
        conn.commit()
        conn.close()

        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from mvp_smoke_check import check_sqlite_tables

        ok, desc = check_sqlite_tables(str(db_path))
        assert not ok
        assert "missing" in desc.lower()

    def test_check_no_alter_table(self):
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from mvp_smoke_check import check_no_alter_table

        ok, desc = check_no_alter_table()
        assert ok, desc


# ---------------------------------------------------------------------------
# 5. Schema baseline: no ALTER TABLE
# ---------------------------------------------------------------------------

class TestSchemaBaseline:
    """Verify no ALTER TABLE migration in ddl.py."""

    def test_no_alter_table_in_ddl(self):
        ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
        content = ddl_path.read_text(encoding="utf-8")
        assert "ALTER TABLE" not in content, "ddl.py must not contain ALTER TABLE migrations"

    def test_source_field_in_baseline(self):
        ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
        content = ddl_path.read_text(encoding="utf-8")
        assert "source TEXT NOT NULL DEFAULT 'api'" in content

    def test_retry_of_job_id_in_baseline(self):
        ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
        content = ddl_path.read_text(encoding="utf-8")
        assert "retry_of_job_id TEXT" in content

    def test_retry_count_in_baseline(self):
        ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
        content = ddl_path.read_text(encoding="utf-8")
        assert "retry_count INTEGER NOT NULL DEFAULT 0" in content

    def test_next_attempt_at_in_baseline(self):
        ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
        content = ddl_path.read_text(encoding="utf-8")
        assert "next_attempt_at TEXT" in content

    def test_scheduled_tables_in_baseline(self):
        ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
        content = ddl_path.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS scheduled_plans" in content
        assert "CREATE TABLE IF NOT EXISTS scheduled_runs" in content
        assert "CREATE TABLE IF NOT EXISTS scheduled_run_steps" in content
