"""Check current Hub state before running commands."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
if not os.path.exists(DB):
    print("DB not found:", DB)
    exit(0)

conn = sqlite3.connect(DB)
c = conn.cursor()

# Business table row counts
biz_tables = [
    'dcp_plan_projects', 'dcp_plan_single_projects',
    'dcp_plan_project_progress', 'dcp_plan_single_project_progress',
    'dcp_plan_bidding_section_progress',
    'dcp_plan_dept_key_personnel',
    'dcp_tower', 'dcp_substation', 'dcp_line_sections', 'dcp_line_branches',
    'dcp_daily_meeting', 'dcp_daily_meeting_snapshot',
]
print("=== Business Table Row Counts ===")
for t in biz_tables:
    try:
        cnt = c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  {t}: {cnt}")
    except Exception as e:
        print(f"  {t}: ERROR {e}")

# Recent jobs
print("\n=== Recent Jobs ===")
try:
    rows = c.execute("SELECT id, ingestion_job_id, parent_job_id, trigger_key, downloader_job_id, status, error, result_json, created_at FROM ingestion_jobs ORDER BY id DESC LIMIT 10").fetchall()
    for r in rows:
        rid, job_id, parent, trigger, dl_id, status, error, result, created = r
        err_short = (error or "")[:80]
        result_info = ""
        if result:
            try:
                rj = json.loads(result)
                result_info = f"collect={rj.get('collect_total','?')}/{rj.get('collect_done','?')}/{rj.get('collect_failed','?')} outbox={rj.get('outbox_delivered','?')}/{rj.get('outbox_failed','?')}"
            except:
                result_info = str(result)[:60]
        print(f"  id={rid} job={str(job_id)[:12]}.. parent={parent} trigger={trigger} dl={str(dl_id)[:12]}.. status={status} err={err_short}")
        if result_info:
            print(f"    {result_info}")
except Exception as e:
    print(f"  Error: {e}")

# Non-terminal jobs
print("\n=== Non-terminal Jobs ===")
try:
    rows = c.execute("SELECT id, trigger_key, status FROM ingestion_jobs WHERE status NOT IN ('succeeded','failed','partial','cancelled')").fetchall()
    if not rows:
        print("  None")
    for r in rows:
        print(f"  id={r[0]} trigger={r[1]} status={r[2]}")
except Exception as e:
    print(f"  Error: {e}")

# Check extra for raw/payload/response/result violations
print("\n=== Extra Field Violations ===")
for t in biz_tables:
    try:
        bad = c.execute(f'SELECT COUNT(*) FROM "{t}" WHERE extra IS NOT NULL AND (extra LIKE "%\\"raw\\"%" OR extra LIKE "%\\"payload\\"%" OR extra LIKE "%\\"response\\"%" OR extra LIKE "%\\"result\\"%")').fetchone()[0]
        if bad > 0:
            print(f"  {t}: {bad} rows with violations!")
    except:
        pass
print("  (no violations = clean)")

conn.close()
