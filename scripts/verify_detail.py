"""Detailed verification of single-project results - v2."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Substation details
print("=== dcp_substation rows ===")
try:
    rows = c.execute("SELECT singleProjectCode, id, prjCode, longitude, latitude FROM dcp_substation").fetchall()
    for r in rows:
        print(f"  project={r[0]} | id={r[1]} | prjCode={r[2]} | lng={r[3]} | lat={r[4]}")
except Exception as e:
    print(f"  Error: {e}")

# line_sections by biddingSectionCode
print("\n=== dcp_line_sections by biddingSectionCode ===")
try:
    rows = c.execute("SELECT biddingSectionCode, COUNT(*) FROM dcp_line_sections GROUP BY biddingSectionCode").fetchall()
    for r in rows:
        print(f"  biddingSection={r[0]}: {r[1]} sections")
except Exception as e:
    print(f"  Error: {e}")

# line_branches by biddingSectionCode
print("\n=== dcp_line_branches by biddingSectionCode ===")
try:
    rows = c.execute("SELECT biddingSectionCode, COUNT(*) FROM dcp_line_branches GROUP BY biddingSectionCode").fetchall()
    for r in rows:
        print(f"  biddingSection={r[0]}: {r[1]} branches")
except Exception as e:
    print(f"  Error: {e}")

# Tower sample
print("\n=== dcp_tower sample (5 rows) ===")
try:
    cols = [r[1] for r in c.execute("PRAGMA table_info(dcp_tower)").fetchall()]
    print(f"  columns: {cols[:8]}...")
    rows = c.execute("SELECT * FROM dcp_tower LIMIT 5").fetchall()
    for r in rows:
        d = dict(zip(cols, r))
        # Show first few meaningful columns
        show = {k: v for k, v in d.items() if not k.startswith('_') and v is not None}
        print(f"  {list(show.items())[:6]}")
except Exception as e:
    print(f"  Error: {e}")

# Check extra field content in substation
print("\n=== dcp_substation extra field sample ===")
try:
    rows = c.execute("SELECT singleProjectCode, extra FROM dcp_substation WHERE extra IS NOT NULL AND extra != '' LIMIT 3").fetchall()
    for r in rows:
        print(f"  project={r[0]} | extra={r[1][:200]}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
