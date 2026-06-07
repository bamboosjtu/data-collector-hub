"""Check fan-out progress."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parent = "ing_refresh_towers_for_current_plan_projects_b9aed8e3d60b"

print("=== Table Counts ===")
for t in ['dcp_tower', 'dcp_substation', 'dcp_line_sections', 'dcp_line_branches']:
    cnt = c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    print(f"  {t}: {cnt}")

print("\n=== Child Jobs Status ===")
rows = c.execute("SELECT status, COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ? GROUP BY status", (parent,)).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

total = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE parent_job_id = ?", (parent,)).fetchone()[0]
print(f"\n  Total children: {total}")

# Check for failed children
print("\n=== Failed Children ===")
rows = c.execute("SELECT ingestion_job_id, params_json, error FROM ingestion_jobs WHERE parent_job_id = ? AND status = 'failed' LIMIT 10", (parent,)).fetchall()
if not rows:
    print("  None")
for r in rows:
    import json
    params = json.loads(r[1]) if r[1] else {}
    print(f"  {r[0][:30]}.. params={params} err={str(r[2])[:100] if r[2] else None}")

conn.close()
