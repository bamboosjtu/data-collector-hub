"""Clean old daily_meeting data and re-run verification."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
c = conn.cursor()

c.execute("delete from dcp_daily_meeting")
print(f"Deleted dcp_daily_meeting: {c.rowcount} rows")

c.execute("delete from dcp_daily_meeting_snapshot")
print(f"Deleted dcp_daily_meeting_snapshot: {c.rowcount} rows")

conn.commit()
conn.close()
print("Done")
