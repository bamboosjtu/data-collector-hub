"""365-day backfill detailed analysis."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Count empty dates (dates in range with 0 rows)
cur.execute("""
    WITH RECURSIVE dates(d) AS (
        SELECT DATE('2025-06-08')
        UNION ALL
        SELECT DATE(d, '+1 day') FROM dates WHERE d < DATE('2026-06-07')
    )
    SELECT d as date, COALESCE(cnt, 0) as row_count
    FROM dates
    LEFT JOIN (SELECT date, COUNT(*) as cnt FROM dcp_daily_meeting GROUP BY date) t
    ON dates.d = t.date
    WHERE COALESCE(cnt, 0) = 0
    ORDER BY d
""")
empty = cur.fetchall()
print(f"Empty dates (0 rows): {len(empty)}")
for r in empty:
    print(f"  {r['date']}")

# 2. Low-data dates (< 10 rows)
cur.execute("""
    SELECT date, COUNT(*) as cnt
    FROM dcp_daily_meeting
    GROUP BY date
    HAVING cnt < 10
    ORDER BY date
""")
low = cur.fetchall()
print(f"\nLow-data dates (< 10 rows): {len(low)}")
for r in low:
    print(f"  {r['date']}: {r['cnt']} rows")

# 3. Total distinct dates
cur.execute("SELECT COUNT(DISTINCT date) FROM dcp_daily_meeting")
print(f"\nTotal distinct dates with data: {cur.fetchone()[0]}")

# 4. Expected 365 days, actual dates
cur.execute("""
    WITH RECURSIVE dates(d) AS (
        SELECT DATE('2025-06-08')
        UNION ALL
        SELECT DATE(d, '+1 day') FROM dates WHERE d < DATE('2026-06-07')
    )
    SELECT COUNT(*) FROM dates
""")
expected = cur.fetchone()[0]
print(f"Expected dates (6/8~6/7): {expected}")

# 5. Dates with data
cur.execute("SELECT COUNT(DISTINCT date) FROM dcp_daily_meeting WHERE date BETWEEN '2025-06-08' AND '2026-06-07'")
actual = cur.fetchone()[0]
print(f"Dates with data: {actual}")
print(f"Empty dates: {expected - actual}")

conn.close()
