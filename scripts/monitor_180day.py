"""Monitor 180-day backfill progress."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

parent_id = "ing_backfill_daily_meetings_by_range_511a5b242a10"

# Parent status
cur.execute("SELECT status, error, result_json FROM ingestion_jobs WHERE ingestion_job_id=?", (parent_id,))
p = cur.fetchone()
if p:
    print(f"Parent: status={p['status']}, error={p['error']}")
    if p['result_json']:
        import json
        r = json.loads(p['result_json'])
        print(f"  result: created={r.get('created_children')}, succeeded={r.get('succeeded')}, failed={r.get('failed')}")
        if 'skipped_remaining_dates' in r:
            print(f"  CIRCUIT BREAKER: skipped_remaining={r['skipped_remaining_dates']}, first_failed={r.get('first_failed_date')}, last_failed={r.get('last_failed_date')}")

# Children summary
cur.execute("SELECT status, COUNT(*) as cnt FROM ingestion_jobs WHERE parent_job_id=? GROUP BY status", (parent_id,))
children = cur.fetchall()
print(f"\nChildren: {[(r['status'], r['cnt']) for r in children]}")

# Total rows
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting")
print(f"dcp_daily_meeting rows: {cur.fetchone()['cnt']}")

conn.close()
