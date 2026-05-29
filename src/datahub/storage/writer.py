from __future__ import annotations

import json
import sqlite3
from typing import Any

from src.datahub.core.specs import TableSpec


def write_table(
    conn: sqlite3.Connection,
    table: TableSpec,
    rows: list[dict[str, Any]],
    scope_values: dict[str, Any],
    payload: dict[str, Any],
    ingestion_job_id: str | None,
) -> dict[str, int]:
    deleted_count = 0
    if table.write_mode == "replace_scope":
        where = " AND ".join(f"{name} = ?" for name in table.scope_column_names)
        values = [scope_values[name] for name in table.scope_column_names]
        deleted_count = conn.execute(f"DELETE FROM {table.table_name} WHERE {where}", values).rowcount

    inserted = 0
    updated = 0
    for index, row in enumerate(rows, start=1):
        before_changes = conn.total_changes
        row_with_meta = dict(row)
        row_with_meta.update(
            {
                "_ingest_message_id": payload["message_id"],
                "_ingest_job_id": ingestion_job_id,
                "_downloader_job_id": payload["downloader_job_id"],
                "_collect_run_id": payload["collect_run_id"],
                "_ingest_row_index": index,
                "_ingest_payload_hash": payload["payload_hash"],
            }
        )
        columns = list(row_with_meta)
        placeholders = ", ".join("?" for _ in columns)
        column_sql = ", ".join(columns)
        values = [_db_value(row_with_meta[column]) for column in columns]
        if table.write_mode in {"upsert", "replace_scope"} and table.primary_key:
            updates = ", ".join(f"{column}=excluded.{column}" for column in columns if column not in table.primary_key)
            conn.execute(
                f"INSERT INTO {table.table_name} ({column_sql}) VALUES ({placeholders}) "
                f"ON CONFLICT({', '.join(table.primary_key)}) DO UPDATE SET {updates}, _ingest_updated_at = CURRENT_TIMESTAMP",
                values,
            )
            inserted += 1
        elif table.write_mode == "append":
            conn.execute(f"INSERT OR IGNORE INTO {table.table_name} ({column_sql}) VALUES ({placeholders})", values)
            inserted += conn.total_changes - before_changes
        else:
            conn.execute(f"INSERT INTO {table.table_name} ({column_sql}) VALUES ({placeholders})", values)
            inserted += 1
    return {"row_count": len(rows), "inserted_count": inserted, "updated_count": updated, "deleted_count": deleted_count}


def public_row(table: TableSpec, row: dict[str, Any]) -> dict[str, Any]:
    return {name: row.get(name) for name in table.columns}


def _db_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value
