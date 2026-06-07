"""Clean up historical dirty substation rows."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

before = c.execute("SELECT COUNT(*) FROM dcp_substation").fetchone()[0]
dirty = c.execute(
    "SELECT COUNT(*) FROM dcp_substation WHERE id IS NULL AND prjCode IS NULL "
    "AND longitude IS NULL AND latitude IS NULL AND longitudeLook IS NULL AND latitudeLook IS NULL"
).fetchone()[0]
print(f"before: {before}, dirty: {dirty}")

c.execute(
    "DELETE FROM dcp_substation WHERE id IS NULL AND prjCode IS NULL "
    "AND longitude IS NULL AND latitude IS NULL AND longitudeLook IS NULL AND latitudeLook IS NULL"
)
conn.commit()

after = c.execute("SELECT COUNT(*) FROM dcp_substation").fetchone()[0]
print(f"after: {after}, deleted: {before - after}")

conn.close()
