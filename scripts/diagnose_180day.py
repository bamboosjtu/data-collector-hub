"""Diagnose 180-day backfill failure."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

parent_id = "ing_backfill_daily_meetings_by_range_d0ef0c42b0bd"

# 1. Child job status distribution
cur.execute("SELECT status, COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? GROUP BY status", (parent_id,))
print("Child job status:", [(r["status"], r["cnt"]) for r in cur.fetchall()])

# 2. Check for errors in child jobs
cur.execute("SELECT ingestion_job_id, status, error FROM ingestion_jobs WHERE parent_job_id=? AND status NOT IN ('succeeded', 'running', 'pending') LIMIT 10", (parent_id,))
rows = cur.fetchall()
if rows:
    print("\nFailed/errored children:")
    for r in rows:
        print(f"  {r['ingestion_job_id']}: {r['status']} - {r['error']}")
else:
    print("\nNo failed/errored children found")

# 3. Check if children are still running
cur.execute("SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? AND status='running'", (parent_id,))
running = cur.fetchone()["cnt"]
cur.execute("SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? AND status='pending'", (parent_id,))
pending = cur.fetchone()["cnt"]
cur.execute("SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? AND status='collecting'", (parent_id,))
collecting = cur.fetchone()["cnt"]
print(f"\nRunning: {running}, Pending: {pending}, Collecting: {collecting}")

# 4. Check for stale children
cur.execute("SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? AND status='stale'", (parent_id,))
stale = cur.fetchone()["cnt"]
print(f"Stale: {stale}")

# 5. Check ingestion_messages for errors
cur.execute("SELECT status, COUNT(*) as cnt FROM ingestion_messages WHERE ingestion_job_id IN (SELECT ingestion_job_id FROM ingestion_jobs WHERE parent_job_id=?) GROUP BY status", (parent_id,))
msgs = cur.fetchall()
print(f"\nIngestion messages status: {[(r['status'], r['cnt']) for r in msgs]}")

# 6. Check for schema_mismatch or other errors
cur.execute("SELECT status, error, COUNT(*) as cnt FROM ingestion_messages WHERE ingestion_job_id IN (SELECT ingestion_job_id FROM ingestion_jobs WHERE parent_job_id=?) AND status != 'succeeded' GROUP BY status, error", (parent_id,))
bad_msgs = cur.fetchall()
if bad_msgs:
    print("\nNon-succeeded messages:")
    for r in bad_msgs:
        print(f"  {r['status']}: {r['error']} (count={r['cnt']})")

conn.close()
