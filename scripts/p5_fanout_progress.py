"""Check fanout progress for scheduler run step 3."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row

# Get step 3 job_id
step = conn.execute(
    "SELECT job_id FROM scheduled_run_steps WHERE run_id='run_dcp_daily_update_e082ac70949a' AND step_order=3"
).fetchone()
if step and step["job_id"]:
    job_id = step["job_id"]
    # Get fanout summary
    items = conn.execute(
        "SELECT status, COUNT(*) as cnt FROM fanout_items WHERE parent_job_id=? GROUP BY status",
        (job_id,)
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) as cnt FROM fanout_items WHERE parent_job_id=?", (job_id,)).fetchone()
    print(f"Step 3 fanout: {job_id}")
    print(f"  Total items: {total['cnt']}")
    for r in items:
        print(f"  {r['status']}: {r['cnt']}")

    # Check parent job status
    job = conn.execute("SELECT status, started_at FROM ingestion_jobs WHERE ingestion_job_id=?", (job_id,)).fetchone()
    if job:
        print(f"  Parent job status: {job['status']} started: {job['started_at']}")

conn.close()
