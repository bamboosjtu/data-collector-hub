"""Check substations fan-out params."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

job_id = "ing_refresh_substations_for_current_plan_projects_f55ef0b8b399"
row = c.execute("SELECT params_json FROM ingestion_jobs WHERE ingestion_job_id = ?", (job_id,)).fetchone()
print(f"Parent params: {row[0]}")

# Count children
total = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ?", (job_id,)).fetchone()[0]
print(f"Children: {total}")

# Status summary
rows = c.execute("SELECT status, COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? GROUP BY status", (job_id,)).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

conn.close()
