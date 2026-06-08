"""Monitor project domain fan-out progress."""
import sqlite3, json

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check all fan-out parents
for cmd in ["refresh_towers_for_current_plan_projects",
            "refresh_substations_for_current_plan_projects",
            "refresh_line_sections_for_current_plan_projects"]:
    cur.execute("SELECT ingestion_job_id, status, error, result_json FROM ingestion_jobs WHERE trigger_key=? ORDER BY started_at DESC LIMIT 1", (cmd,))
    row = cur.fetchone()
    if row:
        print(f"\n{cmd}:")
        print(f"  ID: {row['ingestion_job_id']}")
        print(f"  Status: {row['status']}, Error: {row['error']}")
        if row['result_json']:
            r = json.loads(row['result_json'])
            print(f"  Result: total={r.get('total')}, succeeded={r.get('succeeded')}, failed={r.get('failed')}")

        # Children
        cur.execute("SELECT status, COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? GROUP BY status", (row['ingestion_job_id'],))
        children = cur.fetchall()
        if children:
            print(f"  Children: {[(r['status'], r['cnt']) for r in children]}")

# Table row counts
for tbl in ['dcp_tower', 'dcp_substation', 'dcp_line_sections']:
    cur.execute(f"SELECT COUNT(*) as cnt FROM {tbl}")
    print(f"\n{tbl}: {cur.fetchone()['cnt']} rows")

conn.close()
