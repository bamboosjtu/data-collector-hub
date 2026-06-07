"""Check accepted children - do they have downloader_job_id?"""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parent = "ing_refresh_towers_for_current_plan_projects_b9aed8e3d60b"

# Check accepted children
print("=== Accepted Children (sample) ===")
rows = c.execute("""
    SELECT ingestion_job_id, status, downloader_job_id, params_json
    FROM ingestion_jobs
    WHERE parent_job_id = ? AND status = 'accepted'
    LIMIT 5
""", (parent,)).fetchall()
for r in rows:
    params = json.loads(r[3]) if r[3] else {}
    print(f"  id={r[0][:30]}.. status={r[1]} dl={r[2]} params={params}")

# Check running children
print("\n=== Running Children (sample) ===")
rows = c.execute("""
    SELECT ingestion_job_id, status, downloader_job_id, params_json
    FROM ingestion_jobs
    WHERE parent_job_id = ? AND status = 'running'
    LIMIT 5
""", (parent,)).fetchall()
for r in rows:
    params = json.loads(r[3]) if r[3] else {}
    print(f"  id={r[0][:30]}.. status={r[1]} dl={r[2]} params={params}")

# Count by status
print("\n=== Status Summary ===")
rows = c.execute("SELECT status, COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? GROUP BY status", (parent,)).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

conn.close()
