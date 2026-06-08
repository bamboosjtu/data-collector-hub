"""Acceptance verification for dcp_daily_meeting."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== Daily Meeting Acceptance Check ===\n")

# 1. Total count
cur.execute("SELECT count(*) as cnt FROM dcp_daily_meeting")
total = cur.fetchone()["cnt"]
print(f"1. Total rows: {total}")

# 2. extra NOT NULL
cur.execute("SELECT count(*) as cnt FROM dcp_daily_meeting WHERE extra is not null")
extra_cnt = cur.fetchone()["cnt"]
print(f"2. extra NOT NULL: {extra_cnt} (should be 0)")

# 3. id/date null
cur.execute("SELECT count(*) as cnt FROM dcp_daily_meeting WHERE id is null or date is null")
null_pk = cur.fetchone()["cnt"]
print(f"3. id/date null: {null_pk} (should be 0)")

# 4. count(*) vs count(distinct date:id)
cur.execute("SELECT count(*) as cnt, count(distinct date || ':' || id) as distinct_cnt FROM dcp_daily_meeting")
row = cur.fetchone()
print(f"4. count(*)={row['cnt']}, count(distinct date:id)={row['distinct_cnt']} (should match)")

# 5. Date distribution
cur.execute("SELECT date, count(*) as cnt FROM dcp_daily_meeting GROUP BY date ORDER BY date DESC")
dates = [(r["date"], r["cnt"]) for r in cur.fetchall()]
print(f"5. Date distribution ({len(dates)} dates):")
for d, c in dates:
    print(f"   {d}: {c}")

# 6. ingestion_jobs status
cur.execute("SELECT status, count(*) as cnt FROM ingestion_jobs GROUP BY status")
jobs = [(r["status"], r["cnt"]) for r in cur.fetchall()]
print(f"6. ingestion_jobs status: {jobs}")

# 7. ingestion_messages status
cur.execute("SELECT status, count(*) as cnt FROM ingestion_messages GROUP BY status")
msgs = [(r["status"], r["cnt"]) for r in cur.fetchall()]
print(f"7. ingestion_messages status: {msgs}")

# 8. table_writes status
cur.execute("SELECT status, count(*) as cnt FROM table_writes GROUP BY status")
writes = [(r["status"], r["cnt"]) for r in cur.fetchall()]
print(f"8. table_writes status: {writes}")

# 9. Check for database locked / disk I/O errors in messages
cur.execute("SELECT count(*) as cnt FROM ingestion_messages WHERE error LIKE '%database locked%' OR error LIKE '%disk I/O%'")
db_errors = cur.fetchone()["cnt"]
print(f"9. database locked / disk I/O errors: {db_errors} (should be 0)")

# 10. Check for callback 401/403
cur.execute("SELECT count(*) as cnt FROM ingestion_messages WHERE status LIKE '%401%' OR status LIKE '%403%'")
auth_errors = cur.fetchone()["cnt"]
print(f"10. callback 401/403: {auth_errors} (should be 0)")

# 11. Check for schema_mismatch
cur.execute("SELECT count(*) as cnt FROM ingestion_messages WHERE status = 'schema_mismatch'")
sm = cur.fetchone()["cnt"]
print(f"11. schema_mismatch: {sm} (should be 0)")

# 12. Check for skipped business rows
cur.execute("SELECT count(*) as cnt FROM ingestion_messages WHERE status = 'skipped'")
skipped = cur.fetchone()["cnt"]
print(f"12. skipped messages: {skipped}")

# 13. Key field population
cur.execute("SELECT count(*) as cnt FROM dcp_daily_meeting WHERE singleProjectCode IS NOT NULL")
spc = cur.fetchone()["cnt"]
cur.execute("SELECT count(*) as cnt FROM dcp_daily_meeting WHERE biddingSectionCode IS NOT NULL")
bsc = cur.fetchone()["cnt"]
cur.execute("SELECT count(*) as cnt FROM dcp_daily_meeting WHERE leaderName IS NOT NULL")
ln = cur.fetchone()["cnt"]
print(f"13. Key fields: singleProjectCode={spc}/{total}, biddingSectionCode={bsc}/{total}, leaderName={ln}/{total}")

# 14. Daily avg and max
if dates:
    counts = [c for _, c in dates]
    avg = sum(counts) / len(counts)
    max_c = max(counts)
    min_c = min(counts)
    print(f"14. Daily stats: avg={avg:.1f}, max={max_c}, min={min_c}")

conn.close()
