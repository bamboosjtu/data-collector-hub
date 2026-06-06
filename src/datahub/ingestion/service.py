from __future__ import annotations

import json
import logging
from contextlib import closing
from typing import Any

from src.datahub.core.plugin_loader import NormalizerSpec, PluginSpec, load_normalizer_handler
from src.datahub.storage.sqlite import DataHubStore
from src.datahub.storage.writer import write_table

from .idempotency import classify
from .validator import validate_payload

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, store: DataHubStore, normalizer_map: dict[str, tuple[NormalizerSpec, PluginSpec]] | None = None):
        self.store = store
        self.normalizer_map = normalizer_map or {}
        self._handler_cache: dict[str, Any] = {}

    def ingest_table_batch(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ["message_id", "idempotency_key", "downloader_job_id", "collect_run_id", "dataset_key", "payload_hash", "tables"]
        for key in required:
            if key not in payload:
                return self._failed_response(payload.get("message_id"), "missing_required_field", f"missing field: {key}")
        message_id = str(payload["message_id"])
        with closing(self.store.connect()) as conn:
            existing_message = self.store.get_message(message_id)
            existing_idem = self.store.find_message_by_idempotency_key(str(payload["idempotency_key"]))
            mode = classify(existing_message, existing_idem, payload)
            if mode == "duplicate_accepted":
                return {"status": "duplicate_accepted", "message_id": message_id}
            if mode in {"payload_hash_conflict", "idempotency_conflict"}:
                return self._failed_response(message_id, mode, mode, status="conflict")
            try:
                # Apply normalizers before validation
                expanded_tables = self._apply_normalizers(payload.get("tables") or [])
                expanded_payload = {**payload, "tables": expanded_tables}

                validated = validate_payload(self.store.registry, expanded_payload, self.store.apply_scope_mappings)
                conn.execute("BEGIN")
                self._upsert_writing_message(conn, payload, retry=(mode == "retry"))
                total_rows = 0
                ingestion_job_id = self.store.job_id_for_producer(conn, payload["downloader_job_id"])
                for table, scope_values, rows in validated:
                    stats = write_table(conn, table, rows, scope_values, payload, ingestion_job_id)
                    total_rows += stats["row_count"]
                    conn.execute(
                        """
                        INSERT INTO table_writes(
                          message_id, table_name, dataset_key, scope_values_json, write_mode, status,
                          row_count, inserted_count, updated_count, deleted_count, started_at, finished_at
                        ) VALUES (?, ?, ?, ?, ?, 'succeeded', ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """,
                        (
                            payload["message_id"],
                            table.table_name,
                            table.dataset_key,
                            self._json(scope_values),
                            table.write_mode,
                            stats["row_count"],
                            stats["inserted_count"],
                            stats["updated_count"],
                            stats["deleted_count"],
                        ),
                    )
                conn.execute(
                    """
                    UPDATE ingestion_messages
                    SET status = 'succeeded', row_count = ?, written_at = CURRENT_TIMESTAMP, error = NULL, updated_at = CURRENT_TIMESTAMP
                    WHERE message_id = ?
                    """,
                    (total_rows, payload["message_id"]),
                )
                conn.execute(
                    """
                    UPDATE ingestion_jobs
                    SET status = 'running', message_received = message_received + 1, row_count = row_count + ?, updated_at = CURRENT_TIMESTAMP
                    WHERE downloader_job_id = ?
                    """,
                    (total_rows, payload["downloader_job_id"]),
                )
                conn.commit()
                return {"status": "accepted", "message_id": payload["message_id"], "table_count": len(validated), "row_count": total_rows}
            except ValueError as exc:
                if conn.in_transaction:
                    conn.rollback()
                self._record_failed_message(conn, payload, str(exc))
                return self._error_response(payload.get("message_id"), str(exc))
            except Exception as exc:
                if conn.in_transaction:
                    conn.rollback()
                self._record_failed_message(conn, payload, str(exc), error_code="storage_error")
                return self._failed_response(payload.get("message_id"), "storage_error", str(exc), status="failed")

    def _apply_normalizers(self, tables: list[dict]) -> list[dict]:
        """Expand tables using plugin normalizers before validation.

        For each table payload, if a normalizer is registered for its table_name,
        the normalizer handler is called to produce zero or more output table payloads.
        Tables without normalizers pass through unchanged.
        """
        if not self.normalizer_map:
            return tables

        result: list[dict] = []
        for table_payload in tables:
            table_name = table_payload.get("table_name", "")
            entry = self.normalizer_map.get(table_name)
            if entry is None:
                result.append(table_payload)
                continue

            normalizer, plugin = entry
            handler = self._get_handler(plugin, normalizer)
            scope_values = table_payload.get("scope_values") or {}
            rows = table_payload.get("rows") or []
            try:
                expanded = handler(table_name, scope_values, rows)
                for item in expanded:
                    result.append({
                        "table_name": item.get("table_name", ""),
                        "scope_values": item.get("scope_values", scope_values),
                        "rows": item.get("rows") or [],
                    })
                logger.info("normalizer %s expanded %s -> %d output tables (%d input rows)",
                            normalizer.handler, table_name, len(expanded), len(rows))
            except Exception:
                logger.exception("normalizer %s failed for table %s", normalizer.handler, table_name)
                raise
        return result

    def _get_handler(self, plugin: PluginSpec, normalizer: NormalizerSpec) -> Any:
        cache_key = f"{plugin.name}:{normalizer.handler}"
        if cache_key not in self._handler_cache:
            self._handler_cache[cache_key] = load_normalizer_handler(plugin, normalizer)
        return self._handler_cache[cache_key]

    def _upsert_writing_message(self, conn, payload: dict[str, Any], *, retry: bool) -> None:
        raw_payload = self._json(payload)
        if retry:
            conn.execute(
                """
                UPDATE ingestion_messages
                SET status = 'writing', table_count = ?, row_count = 0, received_payload_json = ?, error = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE message_id = ?
                """,
                (len(payload.get("tables") or []), raw_payload, payload["message_id"]),
            )
            return
        conn.execute(
            """
            INSERT INTO ingestion_messages(
              message_id, idempotency_key, ingestion_job_id, downloader_job_id, collect_run_id,
              dataset_key, scope_key, payload_hash, status, table_count, row_count, received_payload_json
            ) VALUES (?, ?, (SELECT ingestion_job_id FROM ingestion_jobs WHERE downloader_job_id = ?), ?, ?, ?, ?, ?, 'writing', ?, 0, ?)
            """,
            (
                payload["message_id"],
                payload["idempotency_key"],
                payload["downloader_job_id"],
                payload["downloader_job_id"],
                payload["collect_run_id"],
                payload["dataset_key"],
                payload.get("scope_key"),
                payload["payload_hash"],
                len(payload.get("tables") or []),
                raw_payload,
            ),
        )

    def _record_failed_message(self, conn, payload: dict[str, Any], message: str, *, error_code: str | None = None) -> None:
        code = error_code or _error_code(message)
        conn.execute(
            """
            INSERT INTO ingestion_messages(
              message_id, idempotency_key, ingestion_job_id, downloader_job_id, collect_run_id,
              dataset_key, scope_key, payload_hash, status, table_count, row_count, received_payload_json, error
            ) VALUES (?, ?, (SELECT ingestion_job_id FROM ingestion_jobs WHERE downloader_job_id = ?), ?, ?, ?, ?, ?, 'failed', ?, 0, ?, ?)
            ON CONFLICT(message_id) DO UPDATE SET
              status = 'failed', received_payload_json = excluded.received_payload_json, error = excluded.error, updated_at = CURRENT_TIMESTAMP
            """,
            (
                payload.get("message_id"),
                payload.get("idempotency_key"),
                payload.get("downloader_job_id"),
                payload.get("downloader_job_id"),
                payload.get("collect_run_id"),
                payload.get("dataset_key", ""),
                payload.get("scope_key"),
                payload.get("payload_hash", ""),
                len(payload.get("tables") or []),
                self._json(payload),
                f"{code}: {message}",
            ),
        )

    def _error_response(self, message_id: str | None, message: str) -> dict[str, Any]:
        return self._failed_response(message_id, _error_code(message), message)

    def _failed_response(self, message_id: str | None, error_code: str, message: str, *, status: str = "failed") -> dict[str, Any]:
        return {"status": status, "error_code": error_code, "message": message, "message_id": message_id}

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _error_code(message: str) -> str:
    if ":" in message:
        return message.split(":", 1)[0]
    return "invalid_batch"
