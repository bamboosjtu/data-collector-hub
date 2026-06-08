"""Check 7-day backfill parent result."""
import sqlite3, json

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

parent_id = "ing_backfill_daily_meetings_by_range_7640ded141aa"
cur.execute("SELECT result_json, error FROM ingestion_jobs WHERE ingestion_job_id=?", (parent_id,))
row = cur.fetchone()
if row:
    print("Parent result_json:", row["result_json"])
    print("Parent error:", row["error"])

# Check children
cur.execute("SELECT ingestion_job_id, status, params_json, row_count, error FROM ingestion_jobs WHERE parent_job_id=?", (parent_id,))
children = cur.fetchall()
print(f"\nChildren: {len(children)}")
for c in children:
    print(f"  {c['ingestion_job_id']}: status={c['status']}, rows={c['row_count']}, error={c['error']}")
    print(f"    params: {c['params_json']}")

conn.close()
