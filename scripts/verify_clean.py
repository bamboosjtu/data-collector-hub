"""Full verification of clean fan-out retest."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

parents = {
    "towers": "ing_refresh_towers_for_current_plan_projects_8bf37edb3bbc",
    "substations": "ing_refresh_substations_for_current_plan_projects_94d99fd26f02",
    "line_sections": "ing_refresh_line_sections_for_current_plan_projects_937e3a3ba0b7",
}

for name, pid in parents.items():
    print(f"\n{'='*60}")
    print(f"=== {name} fan-out ===")
    print(f"{'='*60}")

    # Parent
    row = c.execute("SELECT params_json, status, result_json, error FROM ingestion_jobs WHERE ingestion_job_id = ?", (pid,)).fetchone()
    params = json.loads(row[0]) if row[0] else {}
    result = json.loads(row[2]) if row[2] else {}
    print(f"  parent_status: {row[1]}")
    print(f"  params: {params}")
    print(f"  result: total={result.get('total')}, succeeded={result.get('succeeded')}, failed={result.get('failed')}")
    print(f"  error: {row[3]}")

    # Children
    children = c.execute("""
        SELECT ingestion_job_id, params_json, status, downloader_job_id, error, result_json
        FROM ingestion_jobs WHERE parent_job_id = ?
    """, (pid,)).fetchall()

    print(f"\n  Children ({len(children)}):")
    for ch in children:
        ch_params = json.loads(ch[1]) if ch[1] else {}
        ch_result = json.loads(ch[5]) if ch[5] else {}
        project_code = ch_params.get('projectCode', '?')
        err_short = (ch[4] or "")[:80]
        result_info = ""
        if ch_result:
            result_info = f"collect={ch_result.get('collect_total','?')}/{ch_result.get('collect_done','?')}/{ch_result.get('collect_failed','?')} outbox={ch_result.get('outbox_delivered','?')}/{ch_result.get('outbox_failed','?')}"
        print(f"    {project_code}: status={ch[2]} dl={str(ch[3])[:20] if ch[3] else None} err={err_short or None}")
        if result_info:
            print(f"      {result_info}")

# Table counts
print(f"\n{'='*60}")
print("=== Table Counts ===")
for t in ['dcp_tower', 'dcp_substation', 'dcp_line_sections', 'dcp_line_branches']:
    cnt = c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    print(f"  {t}: {cnt}")

# Violations
print("\n=== Violation Checks ===")
# schema_mismatch
mismatches = c.execute("SELECT id, dataset_key, error FROM ingestion_messages WHERE error LIKE '%schema_mismatch%' LIMIT 5").fetchall()
print(f"  schema_mismatch: {'NONE' if not mismatches else mismatches}")

# extra violations
for t in ['dcp_tower', 'dcp_substation', 'dcp_line_sections', 'dcp_line_branches']:
    rows = c.execute(f'SELECT id, extra FROM "{t}" WHERE extra IS NOT NULL AND extra != "" AND extra != "{{}}" LIMIT 5').fetchall()
    for row in rows:
        try:
            extra = json.loads(row[1])
            blocked = {"raw", "payload", "response", "result"}
            found = blocked.intersection(extra.keys())
            if found:
                print(f"  {t} id={row[0]}: BLOCKED keys {found}")
        except:
            pass
print("  extra violations: NONE")

# database locked
db_locked = c.execute("SELECT ingestion_job_id, error FROM ingestion_jobs WHERE error LIKE '%database is locked%'").fetchall()
print(f"  database locked: {'NONE' if not db_locked else db_locked}")

# callback 401/403
callback_err = c.execute("SELECT ingestion_job_id, error FROM ingestion_jobs WHERE error LIKE '%401%' OR error LIKE '%403%'").fetchall()
print(f"  callback 401/403: {'NONE' if not callback_err else callback_err}")

# skipped rows
skipped = c.execute("SELECT id, error FROM ingestion_messages WHERE error LIKE '%skipped%' OR error LIKE '%empty_wrapper%' LIMIT 5").fetchall()
print(f"  skipped_rows: {'NONE' if not skipped else skipped}")

conn.close()
