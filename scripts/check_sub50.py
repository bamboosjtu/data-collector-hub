"""Check failed substations children."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parent = "ing_refresh_substations_for_current_plan_projects_727936a83ae6"

# Failed children
print("=== Failed Children ===")
rows = c.execute("""
    SELECT ingestion_job_id, params_json, status, error
    FROM ingestion_jobs
    WHERE parent_job_id = ? AND status = 'failed'
""", (parent,)).fetchall()
for r in rows:
    params = json.loads(r[1]) if r[1] else {}
    print(f"  projectCode={params.get('projectCode', '?')}")
    print(f"  error={r[3]}")
    print()

# Status summary
print("=== Status Summary ===")
rows = c.execute("SELECT status, COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? GROUP BY status", (parent,)).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

conn.close()
