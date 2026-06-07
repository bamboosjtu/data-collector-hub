"""Check year distribution in dcp_plan_projects."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

print("=== year distribution ===")
rows = c.execute("SELECT year, COUNT(*) FROM dcp_plan_projects GROUP BY year").fetchall()
for r in rows:
    print(f"  year={r[0]}: {r[1]}")

# Also check what store.query_table would return
print("\n=== unique prjCode count ===")
rows = c.execute("SELECT COUNT(DISTINCT prjCode) FROM dcp_plan_projects").fetchall()
print(f"  {rows[0][0]} unique prjCodes")

conn.close()
