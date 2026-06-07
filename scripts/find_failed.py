"""Find and retry the failed line_sections child."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Find the failed child
rows = c.execute("""
    SELECT ingestion_job_id, params_json, error
    FROM ingestion_jobs
    WHERE parent_job_id = 'ing_refresh_line_sections_for_current_plan_projects_204b0ba3203d'
      AND status = 'failed'
""").fetchall()
for r in rows:
    print(f"Failed child: {r[0]}")
    print(f"  params: {r[1]}")
    print(f"  error: {r[2]}")

conn.close()
