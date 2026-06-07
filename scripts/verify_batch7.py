"""Verify clean fan-out retest - Batch 7."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Find the latest 3 fan-out parents
parents = c.execute("""
    SELECT ingestion_job_id, trigger_key, params_json, status, result_json, error
    FROM ingestion_jobs
    WHERE trigger_key LIKE '%for_current_plan_projects%'
      AND parent_job_id IS NULL
    ORDER BY id DESC LIMIT 3
""").fetchall()

for row in reversed(parents):  # oldest first
    pid = row[0]
    name = row[1]
    params = json.loads(row[2]) if row[2] else {}
    result = json.loads(row[4]) if row[4] else {}

    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"{'='*60}")
    print(f"  parent_id: {pid}")
    print(f"  params: {params}")
    print(f"  parent_status: {row[3]}")
    print(f"  result: total={result.get('total')}, succeeded={result.get('succeeded')}, failed={result.get('failed')}")
    print(f"  error: {row[5]}")

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
        print(f"    {project_code}: status={ch[2]} err={err_short or None}")
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
mismatches = c.execute("SELECT COUNT(*) FROM ingestion_messages WHERE error LIKE '%schema_mismatch%'").fetchone()[0]
print(f"  schema_mismatch: {mismatches}")

db_locked = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE error LIKE '%database is locked%'").fetchone()[0]
print(f"  database_locked: {db_locked}")

callback_err = c.execute("SELECT COUNT(*) FROM ingestion_jobs WHERE error LIKE '%401%' OR error LIKE '%403%'").fetchone()[0]
print(f"  callback_401_403: {callback_err}")

skipped = c.execute("SELECT COUNT(*) FROM ingestion_messages WHERE error LIKE '%skipped%' OR error LIKE '%empty_wrapper%'").fetchone()[0]
print(f"  skipped_rows: {skipped}")

# Extra violations
violations = 0
for t in ['dcp_tower', 'dcp_substation', 'dcp_line_sections', 'dcp_line_branches']:
    try:
        rows = c.execute(f'SELECT rowid, extra FROM "{t}" WHERE extra IS NOT NULL AND extra != "" AND extra != "{{}}" LIMIT 5').fetchall()
        for row in rows:
            try:
                extra = json.loads(row[1])
                blocked = {"raw", "payload", "response", "result"}
                found = blocked.intersection(extra.keys())
                if found:
                    print(f"  {t} rowid={row[0]}: BLOCKED keys {found}")
                    violations += 1
            except:
                pass
    except:
        pass
print(f"  extra_violations: {violations}")

conn.close()
