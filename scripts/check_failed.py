"""Check failed and stuck children."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Check failed towers child
print("=== Failed towers child ===")
rows = c.execute("""
    SELECT ingestion_job_id, status, error, result_json
    FROM ingestion_jobs
    WHERE parent_job_id = 'ing_refresh_towers_for_current_plan_projects_8bf37edb3bbc'
      AND status = 'failed'
""").fetchall()
for r in rows:
    result = json.loads(r[3]) if r[3] else {}
    print(f"  id={r[0]}")
    print(f"  error={r[2]}")
    print(f"  result={json.dumps(result, indent=2)[:300]}")

# Check accepted line_sections child
print("\n=== Accepted line_sections child ===")
rows = c.execute("""
    SELECT ingestion_job_id, status, downloader_job_id, error, updated_at
    FROM ingestion_jobs
    WHERE parent_job_id = 'ing_refresh_line_sections_for_current_plan_projects_937e3a3ba0b7'
      AND status NOT IN ('succeeded', 'failed', 'partial')
""").fetchall()
for r in rows:
    print(f"  id={r[0]}")
    print(f"  status={r[1]}")
    print(f"  dl_job={r[2]}")
    print(f"  error={r[3]}")
    print(f"  updated_at={r[4]}")

# Check parent status
print("\n=== Parent Status ===")
parents = [
    ("towers", "ing_refresh_towers_for_current_plan_projects_8bf37edb3bbc"),
    ("substations", "ing_refresh_substations_for_current_plan_projects_94d99fd26f02"),
    ("line_sections", "ing_refresh_line_sections_for_current_plan_projects_937e3a3ba0b7"),
]
for name, pid in parents:
    row = c.execute("SELECT status, result_json FROM ingestion_jobs WHERE ingestion_job_id = ?", (pid,)).fetchone()
    result = json.loads(row[1]) if row[1] else {}
    print(f"  {name}: status={row[0]} result_summary={json.dumps(result)[:200]}")

conn.close()
