"""Check fan-out child jobs."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parent = "ing_refresh_towers_for_current_plan_projects_b9aed8e3d60b"

# Check parent params
print("=== Parent Job Params ===")
row = c.execute("SELECT params_json FROM ingestion_jobs WHERE ingestion_job_id = ?", (parent,)).fetchone()
if row:
    print(f"  {row[0]}")

# Check child jobs
print("\n=== Child Jobs (first 10) ===")
rows = c.execute("SELECT ingestion_job_id, status, params_json, error FROM ingestion_jobs WHERE parent_job_id = ? LIMIT 10", (parent,)).fetchall()
for r in rows:
    params = json.loads(r[2]) if r[2] else {}
    print(f"  {r[0][:30]}.. status={r[1]} params={params} err={str(r[3])[:60] if r[3] else None}")

# Count by status
print("\n=== Child Jobs Status Summary ===")
rows = c.execute("SELECT status, COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? GROUP BY status", (parent,)).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

# Total children
total = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ?", (parent,)).fetchone()[0]
print(f"\n  Total children: {total}")

conn.close()
