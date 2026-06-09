"""Analyze table_writes for security domain download speed comparison."""
import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\theTruth\Documents\projects\vibe-demo\data-collector-hub\data\datahub_mvp.db")
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row

# 1. Overall table_writes summary by table
print("=" * 80)
print("TABLE_WRITES SUMMARY BY TABLE")
print("=" * 80)
rows = conn.execute("""
    SELECT table_name,
           COUNT(*) as write_count,
           SUM(row_count) as total_rows,
           MIN(created_at) as first_write,
           MAX(created_at) as last_write
    FROM table_writes
    GROUP BY table_name
    ORDER BY table_name
""").fetchall()
for r in rows:
    print(f"  {r['table_name']:40s} writes={r['write_count']:5d}  rows={r['total_rows']:8d}  "
          f"first={r['first_write']}  last={r['last_write']}")

# 2. dcp_daily_meeting: rows by date (sample)
print("\n" + "=" * 80)
print("DCP_DAILY_MEETING: ROW COUNT BY DATE (sample)")
print("=" * 80)
rows = conn.execute("""
    SELECT substr(date, 1, 10) as d, COUNT(*) as cnt
    FROM dcp_daily_meeting
    WHERE date IS NOT NULL
    GROUP BY d
    ORDER BY d
""").fetchall()
total_days = len(rows)
total_rows = sum(r['cnt'] for r in rows)
print(f"  Total: {total_days} days, {total_rows} rows")
# Print first 5, last 5
for r in rows[:5]:
    print(f"  {r['d']}: {r['cnt']} rows")
if total_days > 10:
    print(f"  ... ({total_days - 10} days omitted) ...")
for r in rows[-5:]:
    print(f"  {r['d']}: {r['cnt']} rows")

# 3. Speed comparison: serial vs concurrent
print("\n" + "=" * 80)
print("SPEED COMPARISON: SERIAL vs CONCURRENT (based on table_writes timestamps)")
print("=" * 80)

# Get all table_writes for dcp_daily_meeting ordered by time
writes = conn.execute("""
    SELECT tw.created_at, tw.row_count, ij.params_json
    FROM table_writes tw
    JOIN ingestion_messages im ON tw.message_id = im.message_id
    JOIN ingestion_jobs ij ON im.ingestion_job_id = ij.ingestion_job_id
    WHERE tw.table_name = 'dcp_daily_meeting'
    ORDER BY tw.created_at
""").fetchall()

if writes:
    first = writes[0]['created_at']
    last = writes[-1]['created_at']
    total_writes = len(writes)
    total_rows_tw = sum(w['row_count'] or 0 for w in writes)
    print(f"  First write: {first}")
    print(f"  Last write:  {last}")
    print(f"  Total writes: {total_writes}")
    print(f"  Total rows:   {total_rows_tw}")

    # Calculate duration
    from datetime import datetime
    try:
        t1 = datetime.strptime(first[:19], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(last[:19], "%Y-%m-%d %H:%M:%S")
        duration_min = (t2 - t1).total_seconds() / 60
        print(f"  Duration:     {duration_min:.1f} minutes")
        if duration_min > 0:
            print(f"  Throughput:   {total_writes / duration_min:.1f} writes/min")
            print(f"  Row rate:     {total_rows_tw / duration_min:.0f} rows/min")
    except:
        pass

# 4. Compare with previous serial run (from ingestion_jobs)
print("\n" + "=" * 80)
print("INGESTION_JOBS: DAILY_MEETING BACKFILL HISTORY")
print("=" * 80)
jobs = conn.execute("""
    SELECT ingestion_job_id, status, created_at, finished_at, result_json,
           params_json, trigger_key
    FROM ingestion_jobs
    WHERE trigger_key LIKE '%daily_meeting%'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()
for j in jobs:
    params = ""
    if j['params_json']:
        try:
            import json
            p = json.loads(j['params_json'])
            params = f"startDate={p.get('startDate','?')} endDate={p.get('endDate','?')}"
        except:
            pass
    finished = j['finished_at'] or 'N/A'
    print(f"  {j['ingestion_job_id'][:50]:50s} status={j['status']:10s} "
          f"created={j['created_at']} finished={finished} {params}")

# 5. Concurrent fan-out job detail
print("\n" + "=" * 80)
print("FANOUT_RUN DETAIL")
print("=" * 80)
runs = conn.execute("""
    SELECT fr.parent_job_id, fr.status, fr.total, fr.max_concurrency,
           fr.consecutive_failures, fr.circuit_opened, fr.created_at, fr.result_json
    FROM fanout_runs fr
""").fetchall()
for r in runs:
    print(f"  parent={r['parent_job_id']}")
    print(f"  status={r['status']} total={r['total']} max_conc={r['max_concurrency']} "
          f"cons_fail={r['consecutive_failures']} circuit={r['circuit_opened']}")
    print(f"  created={r['created_at']}")
    if r['result_json']:
        try:
            import json
            result = json.loads(r['result_json'])
            print(f"  result: succeeded={result.get('succeeded')} failed={result.get('failed')} "
                  f"skipped={result.get('skipped')}")
        except:
            print(f"  result_json: {r['result_json'][:100]}")

# 6. Item completion timeline (10-minute buckets)
print("\n" + "=" * 80)
print("FANOUT_ITEMS COMPLETION TIMELINE (10-min buckets)")
print("=" * 80)
buckets = conn.execute("""
    SELECT substr(updated_at, 1, 16) as bucket,
           COUNT(*) as cnt,
           SUM(CASE WHEN status='succeeded' THEN 1 ELSE 0 END) as ok,
           SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as fail
    FROM fanout_items
    WHERE status IN ('succeeded', 'failed')
    GROUP BY substr(updated_at, 1, 15)
    ORDER BY bucket
""").fetchall()
for b in buckets:
    print(f"  {b['bucket']}: +{b['cnt']} (ok={b['ok']} fail={b['fail']})")

conn.close()
