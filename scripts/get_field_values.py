"""Get actual field values for query_routes testing."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
cur = conn.cursor()

cur.execute("SELECT DISTINCT singleProjectCode FROM dcp_daily_meeting WHERE singleProjectCode IS NOT NULL LIMIT 3")
print("singleProjectCode:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT DISTINCT biddingSectionCode FROM dcp_daily_meeting WHERE biddingSectionCode IS NOT NULL LIMIT 3")
print("biddingSectionCode:", [r[0] for r in cur.fetchall()])

conn.close()
