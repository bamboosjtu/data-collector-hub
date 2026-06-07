"""Check stuck fan-out children."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parent = "ing_refresh_towers_for_current_plan_projects_b9aed8e3d60b"

# Check running children details
print("=== Running Children (sample) ===")
rows = c.execute("""
    SELECT ingestion_job_id, status, downloader_job_id, updated_at
    FROM ingestion_jobs
    WHERE parent_job_id = ? AND status = 'running'
    ORDER BY updated_at ASC LIMIT 5
""", (parent,)).fetchall()
for r in rows:
    print(f"  id={r[0][:30]}.. status={r[1]} dl={str(r[2])[:30] if r[2] else None} updated={r[3]}")

# Check accepted children
print("\n=== Accepted Children (sample) ===")
rows = c.execute("""
    SELECT ingestion_job_id, status, downloader_job_id, updated_at
    FROM ingestion_jobs
    WHERE parent_job_id = ? AND status = 'accepted'
    ORDER BY updated_at ASC LIMIT 5
""", (parent,)).fetchall()
for r in rows:
    print(f"  id={r[0][:30]}.. status={r[1]} dl={str(r[2])[:30] if r[2] else None} updated={r[3]}")

# Check succeeded children count
succeeded = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? AND status = 'succeeded'", (parent,)).fetchone()[0]
print(f"\n=== Succeeded children: {succeeded} ===")

# Check if fan-out handler thread is still alive (check by seeing if new children are being created)
print("\n=== Latest child created_at ===")
row = c.execute("""
    SELECT MAX(created_at) FROM ingestion_jobs WHERE parent_job_id = ?
""", (parent,)).fetchone()
print(f"  Latest: {row[0]}")

conn.close()
