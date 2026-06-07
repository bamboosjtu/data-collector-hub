"""Verify fan-out params and child counts."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parents = [
    "ing_refresh_towers_for_current_plan_projects_8bf37edb3bbc",
    "ing_refresh_substations_for_current_plan_projects_94d99fd26f02",
    "ing_refresh_line_sections_for_current_plan_projects_937e3a3ba0b7",
]

for parent in parents:
    print(f"\n=== {parent[:50]}.. ===")
    row = c.execute("SELECT params_json, status FROM ingestion_jobs WHERE ingestion_job_id = ?", (parent,)).fetchone()
    if row:
        print(f"  params: {row[0]}")
        print(f"  status: {row[1]}")

    # Children
    total = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ?", (parent,)).fetchone()[0]
    print(f"  children: {total}")

    rows = c.execute("SELECT status, COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? GROUP BY status", (parent,)).fetchall()
    for r in rows:
        print(f"    {r[0]}: {r[1]}")

    # Show child projectCodes
    children = c.execute("SELECT params_json, status FROM ingestion_jobs WHERE parent_job_id = ? LIMIT 5", (parent,)).fetchall()
    for ch in children:
        params = json.loads(ch[0]) if ch[0] else {}
        print(f"    projectCode={params.get('projectCode', '?')} status={ch[1]}")

conn.close()
