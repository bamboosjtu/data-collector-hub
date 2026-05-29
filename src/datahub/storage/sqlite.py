from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from src.datahub.core.registry import SchemaRegistry

from .ddl import create_business_table, create_metadata_tables
from .writer import public_row


class DataHubStore:
    def __init__(self, db_path: str | Path, registry: SchemaRegistry, scope_mappings: dict[str, dict[str, str]] | None = None):
        self.db_path = Path(db_path)
        self.registry = registry
        self.scope_mappings = scope_mappings or {}

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with closing(self.connect()) as conn, conn:
            create_metadata_tables(conn)
            for table in self.registry.tables.values():
                create_business_table(conn, table)
            raw = json.dumps(self.registry.as_dict(), ensure_ascii=False, sort_keys=True)
            checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            conn.execute(
                "INSERT OR IGNORE INTO schema_versions(schema_version, registry_json, checksum, active) VALUES (?, ?, ?, 1)",
                (f"v{self.registry.version}", raw, checksum),
            )
            if not conn.execute("SELECT 1 FROM api_keys LIMIT 1").fetchone():
                self.create_api_key("local-admin", ["admin", "ingestion", "query"], token="dev-admin-key", conn=conn)

    def create_ingestion_job(
        self,
        *,
        ingestion_job_id: str,
        producer_job_id: str,
        job_type: str,
        params: dict[str, Any],
        plugin_id: str | None = None,
        dataset_key: str | None = None,
    ) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """
                INSERT INTO ingestion_jobs(ingestion_job_id, plugin_id, trigger_key, downloader_job_id, dataset_key, params_json, status, started_at)
                VALUES (?, ?, ?, ?, ?, ?, 'triggering', CURRENT_TIMESTAMP)
                """,
                (ingestion_job_id, plugin_id, job_type, producer_job_id, dataset_key, self._json(params)),
            )

    def mark_job(
        self,
        ingestion_job_id: str,
        *,
        status: str,
        producer_status: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """
                UPDATE ingestion_jobs
                SET status = ?, producer_status_json = COALESCE(?, producer_status_json),
                    result_json = COALESCE(?, result_json), error = COALESCE(?, error),
                    finished_at = CASE WHEN ? IN ('succeeded','partial','failed','cancelled') THEN CURRENT_TIMESTAMP ELSE finished_at END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE ingestion_job_id = ?
                """,
                (status, self._json(producer_status) if producer_status else None, self._json(result) if result else None, error, status, ingestion_job_id),
            )

    def get_job(self, ingestion_job_id: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM ingestion_jobs WHERE ingestion_job_id = ?", (ingestion_job_id,))

    def get_message(self, message_id: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM ingestion_messages WHERE message_id = ?", (message_id,))

    def find_message_by_idempotency_key(self, idempotency_key: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM ingestion_messages WHERE idempotency_key = ?", (idempotency_key,))

    def list_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._get_rows("SELECT * FROM ingestion_jobs ORDER BY id DESC LIMIT ?", (limit,))

    def list_messages(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._get_rows("SELECT * FROM ingestion_messages ORDER BY id DESC LIMIT ?", (limit,))

    def list_table_writes(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._get_rows("SELECT * FROM table_writes ORDER BY id DESC LIMIT ?", (limit,))

    def query_table(self, table_name: str, filters: dict[str, Any], limit: int = 200) -> list[dict[str, Any]]:
        table = self.registry.require_table(table_name)
        where = []
        params: list[Any] = []
        for key, value in filters.items():
            if value is not None:
                if key not in table.columns:
                    raise ValueError(f"unknown filter column: {key}")
                where.append(f"{key} = ?")
                params.append(value)
        sql = f"SELECT * FROM {table_name}"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY rowid DESC LIMIT ?"
        params.append(limit)
        return [public_row(table, row) for row in self._get_rows(sql, tuple(params))]

    def create_api_key(self, name: str, scopes: list[str], *, token: str | None = None, conn: sqlite3.Connection | None = None) -> dict[str, Any]:
        token = token or f"dh_{secrets.token_urlsafe(24)}"
        key_id = f"key_{secrets.token_hex(8)}"
        active_conn = conn or self.connect()
        owns_conn = conn is None
        try:
            active_conn.execute(
                "INSERT INTO api_keys(key_id, key_hash, name, scopes_json) VALUES (?, ?, ?, ?)",
                (key_id, self.hash_token(token), name, self._json(scopes)),
            )
            if owns_conn:
                active_conn.commit()
        finally:
            if owns_conn:
                active_conn.close()
        return {"key_id": key_id, "token": token, "name": name, "scopes": scopes}

    def verify_api_key(self, token: str | None, required_scope: str) -> bool:
        if not token:
            return False
        row = self._get_row("SELECT scopes_json FROM api_keys WHERE key_hash = ? AND active = 1", (self.hash_token(token),))
        if not row:
            return False
        scopes = json.loads(row["scopes_json"] or "[]")
        return "admin" in scopes or required_scope in scopes

    def apply_scope_mappings(self, table_name: str, scope_values: dict[str, Any]) -> dict[str, Any]:
        mapping = self.scope_mappings.get(table_name)
        if not mapping:
            return scope_values
        result = dict(scope_values)
        for source_key, target_key in mapping.items():
            if source_key in result and target_key not in result:
                result[target_key] = result[source_key]
        return result

    def job_id_for_producer(self, conn: sqlite3.Connection, producer_job_id: str) -> str | None:
        row = conn.execute("SELECT ingestion_job_id FROM ingestion_jobs WHERE downloader_job_id = ?", (producer_job_id,)).fetchone()
        return row["ingestion_job_id"] if row else None

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)

    def _get_row(self, sql: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
        with closing(self.connect()) as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None

    def _get_rows(self, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
        with closing(self.connect()) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]
