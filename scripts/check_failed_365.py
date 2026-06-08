"""Check failed child details for 365-day backfill."""
import sqlite3, json

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

parent_id = "ing_backfill_daily_meetings_by_range_511a5b242a10"

# Find failed children
cur.execute("""
    SELECT ingestion_job_id, status, error, params_json, row_count, message_received
    FROM ingestion_jobs
    WHERE parent_job_id=? AND status='failed'
""", (parent_id,))
failed = cur.fetchall()
print(f"Failed children: {len(failed)}")
for r in failed:
    params = json.loads(r["params_json"])
    print(f"  {r['ingestion_job_id']}: date={params.get('startDate')}, error={r['error']}, rows={r['row_count']}")

# Also check partial children
cur.execute("""
    SELECT ingestion_job_id, status, error, params_json, row_count, message_received
    FROM ingestion_jobs
    WHERE parent_job_id=? AND status='partial'
""", (parent_id,))
partial = cur.fetchall()
if partial:
    print(f"\nPartial children: {len(partial)}")
    for r in partial:
        params = json.loads(r["params_json"])
        print(f"  {r['ingestion_job_id']}: date={params.get('startDate')}, error={r['error']}, rows={r['row_count']}")

# Check circuit breaker status
cur.execute("SELECT error, result_json FROM ingestion_jobs WHERE ingestion_job_id=?", (parent_id,))
p = cur.fetchone()
if p and p["error"]:
    print(f"\nParent error: {p['error']}")

conn.close()
