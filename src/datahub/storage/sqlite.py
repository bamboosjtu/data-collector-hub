from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from src.datahub.core.registry import SchemaRegistry
from src.datahub.core.time_utils import datahub_now_text

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
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def init_schema(self, *, dev_mode: bool = True) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute("PRAGMA journal_mode = WAL")
            create_metadata_tables(conn)
            for table in self.registry.tables.values():
                create_business_table(conn, table)
            raw = json.dumps(self.registry.as_dict(), ensure_ascii=False, sort_keys=True)
            checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            conn.execute(
                "INSERT OR IGNORE INTO schema_versions(schema_version, registry_json, checksum, active, created_at) VALUES (?, ?, ?, 1, ?)",
                (f"v{self.registry.version}", raw, checksum, datahub_now_text()),
            )
            if dev_mode and not conn.execute("SELECT 1 FROM api_keys LIMIT 1").fetchone():
                self.create_api_key("local-admin", ["admin", "ingestion", "query"], token="dev-admin-key", conn=conn)
                self.create_api_key("local-ingestion", ["ingestion"], token="dev-ingestion-key", conn=conn)

    def create_ingestion_job(
        self,
        *,
        ingestion_job_id: str,
        producer_job_id: str,
        job_type: str,
        params: dict[str, Any],
        plugin_id: str | None = None,
        dataset_key: str | None = None,
        parent_job_id: str | None = None,
        retry_of_job_id: str | None = None,
        source: str = "api",
    ) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """
                INSERT INTO ingestion_jobs(ingestion_job_id, parent_job_id, retry_of_job_id, plugin_id, trigger_key, downloader_job_id, dataset_key, params_json, source, status, started_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'triggering', ?, ?, ?)
                """,
                (ingestion_job_id, parent_job_id, retry_of_job_id, plugin_id, job_type, producer_job_id, dataset_key, self._json(params), source, datahub_now_text(), datahub_now_text(), datahub_now_text()),
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
                    finished_at = CASE WHEN ? IN ('succeeded','partial','failed','cancelled') THEN ? ELSE finished_at END,
                    updated_at = ?
                WHERE ingestion_job_id = ?
                """,
                (status, self._json(producer_status) if producer_status else None, self._json(result) if result else None, error, status, datahub_now_text(), datahub_now_text(), ingestion_job_id),
            )

    def get_job(self, ingestion_job_id: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM ingestion_jobs WHERE ingestion_job_id = ?", (ingestion_job_id,))

    def get_message(self, message_id: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM ingestion_messages WHERE message_id = ?", (message_id,))

    def find_message_by_idempotency_key(self, idempotency_key: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM ingestion_messages WHERE idempotency_key = ?", (idempotency_key,))

    def list_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._get_rows("SELECT * FROM ingestion_jobs ORDER BY id DESC LIMIT ?", (limit,))

    def list_child_jobs(self, parent_job_id: str) -> list[dict[str, Any]]:
        return self._get_rows("SELECT * FROM ingestion_jobs WHERE parent_job_id = ? ORDER BY id", (parent_job_id,))

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
                "INSERT INTO api_keys(key_id, key_hash, name, scopes_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (key_id, self.hash_token(token), name, self._json(scopes), datahub_now_text()),
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

    # ── Fan-out scheduler store APIs ──────────────────────────────

    def create_fanout_run_with_items(
        self,
        *,
        parent_job_id: str,
        plugin_id: str,
        parent_command: str,
        child_command: str,
        param_sets: list[dict[str, Any]],
        max_concurrency: int = 1,
        cooldown_seconds: float = 0.0,
        consecutive_failure_threshold: int = 5,
    ) -> None:
        now = datahub_now_text()
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """INSERT INTO fanout_runs(parent_job_id, plugin_id, parent_command, child_command,
                   status, total, max_concurrency, cooldown_seconds, consecutive_failure_threshold,
                   created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'running', ?, ?, ?, ?, ?, ?)""",
                (parent_job_id, plugin_id, parent_command, child_command,
                 len(param_sets), max_concurrency, cooldown_seconds, consecutive_failure_threshold,
                 now, now),
            )
            for idx, params in enumerate(param_sets):
                conn.execute(
                    """INSERT INTO fanout_items(parent_job_id, item_index, params_json, status, created_at, updated_at)
                       VALUES (?, ?, ?, 'pending', ?, ?)""",
                    (parent_job_id, idx, self._json(params), now, now),
                )

    def get_running_fanout_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._get_rows(
            "SELECT * FROM fanout_runs WHERE status = 'running' ORDER BY created_at LIMIT ?",
            (limit,),
        )

    def claim_fanout_run(self, parent_job_id: str, scheduler_id: str, lease_seconds: int = 30) -> bool:
        from src.datahub.core.time_utils import datahub_now
        lease_until = (datahub_now().__class__.fromtimestamp(
            datahub_now().timestamp() + lease_seconds,
            tz=datahub_now().tzinfo,
        )).strftime("%Y-%m-%d %H:%M:%S")
        with closing(self.connect()) as conn, conn:
            cursor = conn.execute(
                """UPDATE fanout_runs
                   SET lease_owner = ?, lease_until = ?, updated_at = ?
                   WHERE parent_job_id = ? AND status = 'running'
                     AND (lease_until IS NULL OR lease_until < ? OR lease_owner = ?)""",
                (scheduler_id, lease_until, datahub_now_text(),
                 parent_job_id, datahub_now_text(), scheduler_id),
            )
            return cursor.rowcount > 0

    def get_fanout_run(self, parent_job_id: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM fanout_runs WHERE parent_job_id = ?", (parent_job_id,))

    def list_submitted_fanout_items(self, parent_job_id: str) -> list[dict[str, Any]]:
        return self._get_rows(
            "SELECT * FROM fanout_items WHERE parent_job_id = ? AND status = 'submitted' ORDER BY item_index",
            (parent_job_id,),
        )

    def reset_stale_submitting_items(self, parent_job_id: str, stale_seconds: int = 120) -> int:
        from src.datahub.core.time_utils import datahub_now
        cutoff = (datahub_now().__class__.fromtimestamp(
            datahub_now().timestamp() - stale_seconds,
            tz=datahub_now().tzinfo,
        )).strftime("%Y-%m-%d %H:%M:%S")
        with closing(self.connect()) as conn, conn:
            cursor = conn.execute(
                """UPDATE fanout_items
                   SET status = 'pending', claimed_by = NULL, claimed_at = NULL, updated_at = ?
                   WHERE parent_job_id = ? AND status = 'submitting'
                     AND claimed_at < ?""",
                (datahub_now_text(), parent_job_id, cutoff),
            )
            return cursor.rowcount

    def claim_next_pending_fanout_item(self, parent_job_id: str, scheduler_id: str) -> dict[str, Any] | None:
        now = datahub_now_text()
        with closing(self.connect()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT id FROM fanout_items
                   WHERE parent_job_id = ? AND status = 'pending'
                     AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
                   ORDER BY item_index LIMIT 1""",
                (parent_job_id, now),
            ).fetchone()
            if row is None:
                conn.rollback()
                return None
            item_id = row["id"]
            cursor = conn.execute(
                """UPDATE fanout_items
                   SET status = 'submitting', claimed_by = ?, claimed_at = ?, updated_at = ?
                   WHERE id = ? AND status = 'pending'""",
                (scheduler_id, now, now, item_id),
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return None
            conn.commit()
            item_row = conn.execute("SELECT * FROM fanout_items WHERE id = ?", (item_id,)).fetchone()
            return dict(item_row) if item_row else None

    def update_fanout_item_submitted(self, item_id: int, *, child_job_id: str) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                "UPDATE fanout_items SET status = 'submitted', child_job_id = ?, updated_at = ? WHERE id = ?",
                (child_job_id, datahub_now_text(), item_id),
            )

    def update_fanout_item_terminal(self, item_id: int, *, status: str, child_job_id: str | None = None, error: str | None = None) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE fanout_items
                   SET status = ?, child_job_id = COALESCE(?, child_job_id), error = COALESCE(?, error), updated_at = ?
                   WHERE id = ?""",
                (status, child_job_id, error, datahub_now_text(), item_id),
            )

    def retry_fanout_item(self, item_id: int, *, error: str, delay_seconds: int) -> None:
        """Reset a fanout_item back to pending for transient retry.

        Increments retry_count, sets next_attempt_at to now + delay_seconds,
        clears child_job_id/claimed_by/claimed_at, and records the error.
        """
        from src.datahub.core.time_utils import datahub_now
        now = datahub_now()
        now_text = now.strftime("%Y-%m-%d %H:%M:%S")
        from datetime import timedelta
        next_attempt = (now + timedelta(seconds=delay_seconds)).strftime("%Y-%m-%d %H:%M:%S")
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE fanout_items
                   SET status = 'pending',
                       child_job_id = NULL,
                       claimed_by = NULL,
                       claimed_at = NULL,
                       retry_count = retry_count + 1,
                       next_attempt_at = ?,
                       error = ?,
                       updated_at = ?
                   WHERE id = ?""",
                (next_attempt, error, now_text, item_id),
            )

    def skip_pending_fanout_items(self, parent_job_id: str) -> int:
        with closing(self.connect()) as conn, conn:
            cursor = conn.execute(
                """UPDATE fanout_items
                   SET status = 'skipped', updated_at = ?
                   WHERE parent_job_id = ? AND status = 'pending'""",
                (datahub_now_text(), parent_job_id),
            )
            return cursor.rowcount

    def get_fanout_stats(self, parent_job_id: str) -> dict[str, int]:
        with closing(self.connect()) as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM fanout_items WHERE parent_job_id = ? GROUP BY status",
                (parent_job_id,),
            ).fetchall()
        counts = {s: 0 for s in ("pending", "submitting", "submitted", "succeeded", "failed", "skipped")}
        for row in rows:
            counts[row["status"]] = row["cnt"]
        return counts

    def get_consecutive_failures(self, parent_job_id: str) -> int:
        with closing(self.connect()) as conn:
            rows = conn.execute(
                """SELECT status FROM fanout_items
                   WHERE parent_job_id = ? AND status IN ('succeeded', 'failed')
                   ORDER BY item_index DESC""",
                (parent_job_id,),
            ).fetchall()
        count = 0
        for row in rows:
            if row["status"] == "failed":
                count += 1
            else:
                break
        return count

    def update_fanout_run_consecutive(self, parent_job_id: str, count: int) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                "UPDATE fanout_runs SET consecutive_failures = ?, updated_at = ? WHERE parent_job_id = ?",
                (count, datahub_now_text(), parent_job_id),
            )

    def mark_fanout_circuit_open(self, parent_job_id: str) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                "UPDATE fanout_runs SET circuit_opened = 1, updated_at = ? WHERE parent_job_id = ?",
                (datahub_now_text(), parent_job_id),
            )

    def update_fanout_run_submit(self, parent_job_id: str, last_submit_at: str) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                "UPDATE fanout_runs SET last_submit_at = ?, updated_at = ? WHERE parent_job_id = ?",
                (last_submit_at, datahub_now_text(), parent_job_id),
            )

    def close_fanout_run(self, parent_job_id: str, status: str, result: dict[str, Any] | None = None) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE fanout_runs
                   SET status = ?, result_json = COALESCE(?, result_json), lease_owner = NULL, lease_until = NULL, updated_at = ?
                   WHERE parent_job_id = ?""",
                (status, self._json(result) if result else None, datahub_now_text(), parent_job_id),
            )

    def has_fanout_run(self, parent_job_id: str) -> bool:
        row = self._get_row("SELECT 1 FROM fanout_runs WHERE parent_job_id = ?", (parent_job_id,))
        return row is not None

    def find_active_retry(self, retry_of_job_id: str) -> dict[str, Any] | None:
        """Find an active (non-terminal) retry job for the given original job."""
        return self._get_row(
            """SELECT * FROM ingestion_jobs
               WHERE retry_of_job_id = ? AND status NOT IN ('succeeded','partial','failed','cancelled')
               ORDER BY created_at DESC LIMIT 1""",
            (retry_of_job_id,),
        )

    def list_failed_fanout_items(self, parent_job_id: str, item_indexes: list[int] | None = None) -> list[dict[str, Any]]:
        """List fanout_items eligible for retry: failed/skipped, or with failed/partial/cancelled child job."""
        items = self._get_rows(
            """SELECT fi.* FROM fanout_items fi
               WHERE fi.parent_job_id = ? AND fi.status IN ('failed', 'skipped')
               ORDER BY fi.item_index""",
            (parent_job_id,),
        )
        # Also include items whose child job is in a retryable terminal state
        child_items = self._get_rows(
            """SELECT fi.* FROM fanout_items fi
               JOIN ingestion_jobs ij ON fi.child_job_id = ij.ingestion_job_id
               WHERE fi.parent_job_id = ? AND ij.status IN ('failed', 'partial', 'cancelled')
               AND fi.status NOT IN ('pending', 'submitting', 'submitted')
               ORDER BY fi.item_index""",
            (parent_job_id,),
        )
        # Merge, deduplicate by id
        seen = set()
        result = []
        for item in items + child_items:
            if item["id"] not in seen:
                seen.add(item["id"])
                result.append(item)
        # Filter by item_indexes if provided
        if item_indexes is not None:
            index_set = set(item_indexes)
            result = [item for item in result if item["item_index"] in index_set]
        return result

    def update_fanout_item_for_retry(self, item_id: int, *, new_child_job_id: str) -> None:
        """Reset a fanout_item for retry: set status to submitted, update child_job_id, increment retry_count."""
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE fanout_items
                   SET status = 'submitted',
                       child_job_id = ?,
                       error = NULL,
                       claimed_by = NULL,
                       claimed_at = NULL,
                       retry_count = retry_count + 1,
                       next_attempt_at = NULL,
                       updated_at = ?
                   WHERE id = ?""",
                (new_child_job_id, datahub_now_text(), item_id),
            )

    def reopen_fanout_run(self, parent_job_id: str) -> None:
        """Reopen a closed fanout_run back to running status."""
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE fanout_runs
                   SET status = 'running',
                       result_json = NULL,
                       lease_owner = NULL,
                       lease_until = NULL,
                       updated_at = ?
                   WHERE parent_job_id = ?""",
                (datahub_now_text(), parent_job_id),
            )

    def reopen_parent_ingestion_job(self, ingestion_job_id: str) -> None:
        """Reopen a parent ingestion_job: set running, clear error/result_json/finished_at."""
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE ingestion_jobs
                   SET status = 'running',
                       error = NULL,
                       result_json = NULL,
                       finished_at = NULL,
                       updated_at = ?
                   WHERE ingestion_job_id = ?""",
                (datahub_now_text(), ingestion_job_id),
            )

    def list_job_retries(self, ingestion_job_id: str) -> list[dict[str, Any]]:
        """List all retry jobs for the given original job."""
        return self._get_rows(
            "SELECT * FROM ingestion_jobs WHERE retry_of_job_id = ? ORDER BY created_at",
            (ingestion_job_id,),
        )

    def list_fanout_items_with_child_jobs(self, parent_job_id: str) -> list[dict[str, Any]]:
        """List fanout_items joined with child ingestion_jobs for fanout detail API."""
        return self._get_rows(
            """SELECT
                 fi.id as item_id,
                 fi.item_index,
                 fi.status as item_status,
                 fi.retry_count,
                 fi.child_job_id,
                 fi.error as item_error,
                 fi.params_json,
                 ij.ingestion_job_id,
                 ij.status as child_status,
                 ij.source as child_source,
                 ij.retry_of_job_id as child_retry_of_job_id,
                 ij.error as child_error
               FROM fanout_items fi
               LEFT JOIN ingestion_jobs ij ON fi.child_job_id = ij.ingestion_job_id
               WHERE fi.parent_job_id = ?
               ORDER BY fi.item_index""",
            (parent_job_id,),
        )

    # ── Collection plan store APIs ──────────────────────────────

    def upsert_scheduled_plan(
        self,
        *,
        plan_name: str,
        enabled: int = 0,
        schedule_type: str = "daily",
        schedule_time: str | None = None,
        timezone: str = "Asia/Shanghai",
        config_json: str,
        next_run_at: str | None = None,
    ) -> None:
        now = datahub_now_text()
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """INSERT INTO scheduled_plans(plan_name, enabled, schedule_type, schedule_time, timezone, config_json, next_run_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(plan_name) DO UPDATE SET
                     enabled = excluded.enabled,
                     schedule_type = excluded.schedule_type,
                     schedule_time = excluded.schedule_time,
                     timezone = excluded.timezone,
                     config_json = excluded.config_json,
                     next_run_at = COALESCE(excluded.next_run_at, scheduled_plans.next_run_at),
                     updated_at = excluded.updated_at""",
                (plan_name, enabled, schedule_type, schedule_time, timezone, config_json, next_run_at, now, now),
            )

    def get_scheduled_plan(self, plan_name: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM scheduled_plans WHERE plan_name = ?", (plan_name,))

    def list_scheduled_plans(self) -> list[dict[str, Any]]:
        return self._get_rows("SELECT * FROM scheduled_plans ORDER BY plan_name", ())

    def update_plan_last_run(self, plan_name: str, *, run_id: str, status: str, next_run_at: str | None = None) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """UPDATE scheduled_plans
                   SET last_run_id = ?, last_status = ?, last_run_at = ?,
                       next_run_at = COALESCE(?, next_run_at), updated_at = ?
                   WHERE plan_name = ?""",
                (run_id, status, datahub_now_text(), next_run_at, datahub_now_text(), plan_name),
            )

    def update_plan_next_run(self, plan_name: str, next_run_at: str | None) -> None:
        with closing(self.connect()) as conn, conn:
            conn.execute(
                "UPDATE scheduled_plans SET next_run_at = ?, updated_at = ? WHERE plan_name = ?",
                (next_run_at, datahub_now_text(), plan_name),
            )

    def create_scheduled_run(
        self,
        *,
        run_id: str,
        plan_name: str,
        trigger_source: str,
        status: str = "running",
    ) -> None:
        now = datahub_now_text()
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """INSERT INTO scheduled_runs(run_id, plan_name, trigger_source, status, started_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (run_id, plan_name, trigger_source, status, now, now, now),
            )

    def update_scheduled_run(
        self,
        run_id: str,
        *,
        status: str | None = None,
        result_json: str | None = None,
        error: str | None = None,
    ) -> None:
        with closing(self.connect()) as conn, conn:
            finished = datahub_now_text() if status and status in ("succeeded", "partial", "failed", "skipped") else None
            conn.execute(
                """UPDATE scheduled_runs
                   SET status = COALESCE(?, status),
                       result_json = COALESCE(?, result_json),
                       error = COALESCE(?, error),
                       finished_at = COALESCE(?, finished_at),
                       updated_at = ?
                   WHERE run_id = ?""",
                (status, result_json, error, finished, datahub_now_text(), run_id),
            )

    def get_scheduled_run(self, run_id: str) -> dict[str, Any] | None:
        return self._get_row("SELECT * FROM scheduled_runs WHERE run_id = ?", (run_id,))

    def list_scheduled_runs(self, plan_name: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if plan_name:
            return self._get_rows(
                "SELECT * FROM scheduled_runs WHERE plan_name = ? ORDER BY created_at DESC LIMIT ?",
                (plan_name, limit),
            )
        return self._get_rows(
            "SELECT * FROM scheduled_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

    def get_running_plan_run(self, plan_name: str) -> dict[str, Any] | None:
        return self._get_row(
            "SELECT * FROM scheduled_runs WHERE plan_name = ? AND status = 'running' ORDER BY created_at DESC LIMIT 1",
            (plan_name,),
        )

    def create_scheduled_run_step(
        self,
        *,
        run_id: str,
        step_order: int,
        command_name: str,
        params_json: str,
        status: str = "pending",
        wait_for_terminal: int = 1,
    ) -> None:
        now = datahub_now_text()
        with closing(self.connect()) as conn, conn:
            conn.execute(
                """INSERT INTO scheduled_run_steps(run_id, step_order, command_name, params_json, status, wait_for_terminal, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (run_id, step_order, command_name, params_json, status, wait_for_terminal, now, now),
            )

    def update_scheduled_run_step(
        self,
        step_id: int,
        *,
        status: str | None = None,
        job_id: str | None = None,
        result_json: str | None = None,
        error: str | None = None,
    ) -> None:
        with closing(self.connect()) as conn, conn:
            finished = datahub_now_text() if status and status in ("succeeded", "partial", "failed", "skipped") else None
            conn.execute(
                """UPDATE scheduled_run_steps
                   SET status = COALESCE(?, status),
                       job_id = COALESCE(?, job_id),
                       result_json = COALESCE(?, result_json),
                       error = COALESCE(?, error),
                       started_at = CASE WHEN ? IS NOT NULL AND started_at IS NULL THEN ? ELSE started_at END,
                       finished_at = COALESCE(?, finished_at),
                       updated_at = ?
                   WHERE id = ?""",
                (status, job_id, result_json, error, status, datahub_now_text(), finished, datahub_now_text(), step_id),
            )

    def get_scheduled_run_steps(self, run_id: str) -> list[dict[str, Any]]:
        return self._get_rows(
            "SELECT * FROM scheduled_run_steps WHERE run_id = ? ORDER BY step_order",
            (run_id,),
        )

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
