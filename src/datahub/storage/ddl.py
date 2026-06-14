from __future__ import annotations

import sqlite3

from src.datahub.core.specs import TableSpec


INGEST_META_COLUMNS = {
    "_ingest_message_id": "TEXT",
    "_ingest_job_id": "TEXT",
    "_downloader_job_id": "TEXT",
    "_collect_run_id": "TEXT",
    "_ingest_row_index": "INTEGER",
    "_ingest_payload_hash": "TEXT",
    "_ingest_created_at": "TEXT",
    "_ingest_updated_at": "TEXT",
}


def _migrate_fanout_items_columns(conn: sqlite3.Connection) -> None:
    """Add retry_count and next_attempt_at columns to fanout_items if missing."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(fanout_items)").fetchall()}
    if "retry_count" not in existing:
        conn.execute("ALTER TABLE fanout_items ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0")
    if "next_attempt_at" not in existing:
        conn.execute("ALTER TABLE fanout_items ADD COLUMN next_attempt_at TEXT")


def create_metadata_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ingestion_jobs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ingestion_job_id TEXT NOT NULL UNIQUE,
          parent_job_id TEXT,
          plugin_id TEXT,
          trigger_key TEXT,
          downloader_job_id TEXT UNIQUE,
          dataset_key TEXT,
          params_json TEXT NOT NULL,
          source TEXT NOT NULL DEFAULT 'api',
          status TEXT NOT NULL,
          message_total INTEGER DEFAULT 0,
          message_received INTEGER DEFAULT 0,
          message_failed INTEGER DEFAULT 0,
          row_count INTEGER DEFAULT 0,
          producer_status_json TEXT,
          result_json TEXT,
          error TEXT,
          started_at TEXT,
          finished_at TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ingestion_messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          message_id TEXT NOT NULL UNIQUE,
          idempotency_key TEXT NOT NULL UNIQUE,
          ingestion_job_id TEXT,
          downloader_job_id TEXT,
          collect_run_id TEXT,
          dataset_key TEXT NOT NULL,
          scope_key TEXT,
          payload_hash TEXT NOT NULL,
          status TEXT NOT NULL,
          table_count INTEGER DEFAULT 0,
          row_count INTEGER DEFAULT 0,
          received_payload_json TEXT,
          error TEXT,
          received_at TEXT,
          written_at TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS table_writes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          message_id TEXT NOT NULL,
          table_name TEXT NOT NULL,
          dataset_key TEXT,
          scope_values_json TEXT,
          write_mode TEXT NOT NULL,
          status TEXT NOT NULL,
          row_count INTEGER DEFAULT 0,
          inserted_count INTEGER DEFAULT 0,
          updated_count INTEGER DEFAULT 0,
          deleted_count INTEGER DEFAULT 0,
          error TEXT,
          started_at TEXT,
          finished_at TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS schema_versions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          schema_version TEXT NOT NULL UNIQUE,
          registry_json TEXT NOT NULL,
          checksum TEXT NOT NULL,
          active INTEGER DEFAULT 0,
          created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS api_keys (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          key_id TEXT NOT NULL UNIQUE,
          key_hash TEXT NOT NULL UNIQUE,
          name TEXT NOT NULL,
          scopes_json TEXT NOT NULL,
          active INTEGER DEFAULT 1,
          created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS fanout_runs (
          parent_job_id TEXT PRIMARY KEY,
          plugin_id TEXT NOT NULL,
          parent_command TEXT NOT NULL,
          child_command TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'running',
          total INTEGER NOT NULL,
          max_concurrency INTEGER NOT NULL DEFAULT 1,
          cooldown_seconds REAL NOT NULL DEFAULT 0,
          consecutive_failure_threshold INTEGER NOT NULL DEFAULT 5,
          consecutive_failures INTEGER NOT NULL DEFAULT 0,
          circuit_opened INTEGER NOT NULL DEFAULT 0,
          last_submit_at TEXT,
          result_json TEXT,
          lease_owner TEXT,
          lease_until TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fanout_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          parent_job_id TEXT NOT NULL,
          item_index INTEGER NOT NULL,
          params_json TEXT NOT NULL,
          child_job_id TEXT,
          status TEXT NOT NULL DEFAULT 'pending',
          error TEXT,
          claimed_by TEXT,
          claimed_at TEXT,
          retry_count INTEGER NOT NULL DEFAULT 0,
          next_attempt_at TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          UNIQUE(parent_job_id, item_index),
          FOREIGN KEY(parent_job_id) REFERENCES fanout_runs(parent_job_id)
        );
        CREATE INDEX IF NOT EXISTS idx_fanout_runs_status_lease
          ON fanout_runs(status, lease_until);
        CREATE INDEX IF NOT EXISTS idx_fanout_items_parent_status_index
          ON fanout_items(parent_job_id, status, item_index);
        CREATE INDEX IF NOT EXISTS idx_fanout_items_child_job
          ON fanout_items(child_job_id);
        """
    )

    # Safe migration: add retry_count and next_attempt_at to fanout_items
    # if they don't exist (for existing databases).
    _migrate_fanout_items_columns(conn)


def create_business_table(conn: sqlite3.Connection, table: TableSpec) -> None:
    column_sql: list[str] = []
    for column in table.columns.values():
        null_sql = "NULL" if column.nullable else "NOT NULL"
        column_sql.append(f"{column.name} {_sqlite_type(column.type)} {null_sql}")
    for name, definition in INGEST_META_COLUMNS.items():
        column_sql.append(f"{name} {definition}")
    constraints: list[str] = []
    if table.primary_key:
        constraints.append(f"UNIQUE({', '.join(table.primary_key)})")
    if table.write_mode == "append":
        constraints.append("UNIQUE(_ingest_message_id, _ingest_row_index)")
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table.table_name} ({', '.join(column_sql + constraints)})")
    for name in table.scope_column_names:
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table.table_name}_{name} ON {table.table_name}({name})")


def _sqlite_type(column_type: str) -> str:
    return {"integer": "INTEGER", "number": "REAL", "json": "TEXT"}.get(column_type, "TEXT")
