"""Clean up historical dirty substation rows (all key fields NULL)."""
import argparse
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "datahub_mvp.db"


def main():
    parser = argparse.ArgumentParser(description="Clean dirty substation rows")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
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


if __name__ == "__main__":
    main()
