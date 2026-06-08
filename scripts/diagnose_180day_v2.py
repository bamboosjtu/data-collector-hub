"""Deeper diagnosis: check child job details."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

parent_id = "ing_backfill_daily_meetings_by_range_d0ef0c42b0bd"

# 1. Check child job details
cur.execute("""
    SELECT ingestion_job_id, status, downloader_job_id, params_json, error,
           message_total, message_received, message_failed, row_count,
           started_at, finished_at
    FROM ingestion_jobs
    WHERE parent_job_id=?
    LIMIT 5
""", (parent_id,))
rows = cur.fetchall()
for r in rows:
    print(f"Job: {r['ingestion_job_id']}")
    print(f"  Status: {r['status']}, downloader_job_id: {r['downloader_job_id']}")
    print(f"  Params: {r['params_json']}")
    print(f"  Error: {r['error']}")
    print(f"  Messages: total={r['message_total']}, received={r['message_received']}, failed={r['message_failed']}")
    print(f"  Rows: {r['row_count']}")
    print(f"  Started: {r['started_at']}, Finished: {r['finished_at']}")
    print()

# 2. Check if there are any succeeded child jobs from this parent
cur.execute("SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? AND status='succeeded'", (parent_id,))
print(f"Succeeded children: {cur.fetchone()['cnt']}")

# 3. Check the parent job details
cur.execute("SELECT * FROM ingestion_jobs WHERE ingestion_job_id=?", (parent_id,))
p = cur.fetchone()
if p:
    print(f"\nParent job:")
    print(f"  Status: {p['status']}")
    print(f"  Result: {p['result_json']}")
    print(f"  Error: {p['error']}")
    print(f"  Started: {p['started_at']}, Finished: {p['finished_at']}")

conn.close()
