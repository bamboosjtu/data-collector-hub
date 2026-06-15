#!/usr/bin/env python3
"""Manual SQLite backup script using the online backup API."""

import argparse
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Back up a SQLite database using the online backup API.")
    parser.add_argument("--db", default=os.environ.get("DATAHUB_DB_PATH", "data/datahub_mvp.db"),
                        help="Path to the SQLite database file (default: DATAHUB_DB_PATH env or data/datahub_mvp.db)")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Error: database file not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent
    backup_dir = project_root / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"datahub_{timestamp}.sqlite"

    try:
        src = sqlite3.connect(str(db_path))
        dst = sqlite3.connect(str(backup_path))
        src.backup(dst)
        dst.close()
        src.close()
    except Exception as exc:
        print(f"Error: backup failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not backup_path.exists() or backup_path.stat().st_size == 0:
        print("Error: backup file is missing or empty", file=sys.stderr)
        sys.exit(1)

    print(backup_path)


if __name__ == "__main__":
    main()
