import sqlite3
import json
from pathlib import Path

db_path = Path("data") / "collector.db"

print("DB:", db_path.resolve())
print("DB exists:", db_path.exists())

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

def show(title, sql, params=()):
    print("\n== " + title + " ==")
    rows = conn.execute(sql, params).fetchall()
    if not rows:
        print("(empty)")
        return
    for row in rows:
        print(dict(row))

show(
    "raw_events by dataset/status",
    """
    SELECT dataset_key, processing_status, COUNT(1) AS count
    FROM raw_events
    GROUP BY dataset_key, processing_status
    ORDER BY dataset_key, processing_status
    """
)

show(
    "latest batches",
    """
    SELECT batch_id, batch_key, status, raw_record_count, error_count, created_at
    FROM collection_batches
    ORDER BY id DESC
    LIMIT 5
    """
)

show(
    "latest commands",
    """
    SELECT command_run_id, command_key, dataset_keys, profile, status,
           request_count, raw_record_count, error_count
    FROM collection_commands
    ORDER BY id DESC
    LIMIT 5
    """
)

show(
    "latest requests",
    """
    SELECT request_id, request_key, dataset_key, request_kind, api_name,
           status, raw_record_count, error_count
    FROM collection_requests
    ORDER BY id DESC
    LIMIT 5
    """
)

show(
    "latest raw events",
    """
    SELECT id, raw_event_key, dataset_key, processing_status,
           batch_id, command_run_id, request_id, source_record_id
    FROM raw_events
    ORDER BY id DESC
    LIMIT 5
    """
)

row = conn.execute("""
    SELECT raw_record
    FROM raw_events
    ORDER BY id DESC
    LIMIT 1
""").fetchone()

print("\n== latest raw_record ==")
if row:
    try:
        print(json.dumps(json.loads(row["raw_record"]), ensure_ascii=False, indent=2))
    except Exception:
        print(row["raw_record"])
else:
    print("(empty)")
