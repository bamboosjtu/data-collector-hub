"""Verification script for daily_meeting field-based schema."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Row counts
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting")
dm_cnt = cur.fetchone()["cnt"]
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting_snapshot")
dms_cnt = cur.fetchone()["cnt"]

# 2. Date distribution
cur.execute("SELECT date, COUNT(*) as cnt FROM dcp_daily_meeting GROUP BY date ORDER BY date")
dm_dates = [(r["date"], r["cnt"]) for r in cur.fetchall()]

# 3. Extra field
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting WHERE extra IS NOT NULL")
dm_extra = cur.fetchone()["cnt"]
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting_snapshot WHERE extra IS NOT NULL")
dms_extra = cur.fetchone()["cnt"]

# 4. Key business fields
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting WHERE singleProjectCode IS NOT NULL")
dm_spc = cur.fetchone()["cnt"]
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting WHERE biddingSectionCode IS NOT NULL")
dm_bsc = cur.fetchone()["cnt"]
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting WHERE leaderName IS NOT NULL")
dm_ln = cur.fetchone()["cnt"]

# 5. Schema mismatch
cur.execute("SELECT COUNT(*) as cnt FROM ingestion_messages WHERE status = 'schema_mismatch'")
sm_cnt = cur.fetchone()["cnt"]

# 6. Wrapper fields check
cur.execute("PRAGMA table_info(dcp_daily_meeting)")
dm_cols = [r[1] for r in cur.fetchall()]
wrapper_cols = [c for c in ["code", "message", "success", "traceId", "data"] if c in dm_cols]

# 7. Snapshot key fields
cur.execute("SELECT COUNT(*) as cnt FROM dcp_daily_meeting_snapshot WHERE singleProjectCode IS NOT NULL")
dms_spc = cur.fetchone()["cnt"]

print(f"=== Daily Meeting Verification ===")
print(f"dcp_daily_meeting: {dm_cnt} rows, {len(dm_dates)} dates")
print(f"dcp_daily_meeting_snapshot: {dms_cnt} rows")
print(f"extra NOT NULL: daily_meeting={dm_extra}, snapshot={dms_extra}")
print(f"singleProjectCode NOT NULL: daily_meeting={dm_spc}/{dm_cnt}, snapshot={dms_spc}/{dms_cnt}")
print(f"biddingSectionCode NOT NULL: {dm_bsc}/{dm_cnt}")
print(f"leaderName NOT NULL: {dm_ln}/{dm_cnt}")
print(f"schema_mismatch count: {sm_cnt}")
print(f"wrapper cols in schema: {wrapper_cols} (should be empty)")
print(f"date distribution: {dm_dates[:5]}...{dm_dates[-3:]}")

conn.close()
