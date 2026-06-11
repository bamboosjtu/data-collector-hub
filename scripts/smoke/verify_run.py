"""Verify a command run: check table counts, extra violations, skipped_rows, schema_mismatch."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "datahub_mvp.db"

biz_tables = [
    'dcp_plan_year_project', 'dcp_plan_year_single_project',
    'dcp_plan_project_progress', 'dcp_plan_single_project_progress',
    'dcp_plan_bidsection_progress',
    'dcp_plan_dept_key_personnel',
    'dcp_project_tower', 'dcp_project_substation', 'dcp_project_line_sections', 'dcp_project_line_branches',
    'dcp_safe_daily_meeting', 'dcp_safe_daily_meeting_snapshot',
]


def main():
    parser = argparse.ArgumentParser(description="Verify command run results")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path")
    parser.add_argument("job_id", nargs="?", help="Ingestion job ID to inspect")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    c = conn.cursor()

    print("=== Business Table Row Counts ===")
    for t in biz_tables:
        try:
            cnt = c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            print(f"  {t}: {cnt}")
        except Exception as e:
            print(f"  {t}: ERROR {e}")

    if args.job_id:
        job_id = args.job_id

        print(f"\n=== Messages for job {job_id[:30]}.. ===")
        try:
            msgs = c.execute("SELECT id, message_id, dataset_key, status, row_count, error FROM ingestion_messages WHERE ingestion_job_id = ?", (job_id,)).fetchall()
            for m in msgs:
                err_short = (m[5] or "")[:100]
                print(f"  id={m[0]} msg_id={str(m[1])[:20]}.. dataset={m[2]} status={m[3]} rows={m[4]} err={err_short}")
        except Exception as e:
            print(f"  Error: {e}")

        print(f"\n=== Table Writes ===")
        try:
            writes = c.execute("""
                SELECT tw.table_name, tw.write_mode, tw.status, tw.row_count, tw.inserted_count, tw.updated_count, tw.error
                FROM table_writes tw
                JOIN ingestion_messages im ON tw.message_id = im.message_id
                WHERE im.ingestion_job_id = ?
            """, (job_id,)).fetchall()
            for w in writes:
                err_short = (w[6] or "")[:80]
                print(f"  table={w[0]} mode={w[1]} status={w[2]} rows={w[3]} ins={w[4]} upd={w[5]} err={err_short}")
        except Exception as e:
            print(f"  Error: {e}")

        print(f"\n=== Skipped Rows Check ===")
        try:
            skipped = c.execute("SELECT id, dataset_key, error FROM ingestion_messages WHERE ingestion_job_id = ? AND error IS NOT NULL AND error != ''", (job_id,)).fetchall()
            if not skipped:
                print("  No errors in messages")
            for s in skipped:
                print(f"  msg={s[0]} dataset={s[1]} err={str(s[2])[:120]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Extra violations check
    print("\n=== Extra Field Violations (raw/payload/response/result) ===")
    violations = 0
    for t in biz_tables:
        try:
            rows = c.execute(f'SELECT id, extra FROM "{t}" WHERE extra IS NOT NULL AND extra != "" AND extra != "{{}}" LIMIT 10').fetchall()
            for row in rows:
                try:
                    extra = json.loads(row[1])
                    blocked = {"raw", "payload", "response", "result"}
                    found = blocked.intersection(extra.keys())
                    if found:
                        print(f"  {t} id={row[0]}: BLOCKED keys found: {found}")
                        violations += 1
                except Exception:
                    pass
        except Exception:
            pass
    if violations == 0:
        print("  Clean - no violations")

    # Check for schema_mismatch in ingestion_messages
    print("\n=== Schema Mismatch Check ===")
    try:
        mismatches = c.execute("SELECT id, dataset_key, error FROM ingestion_messages WHERE error LIKE '%schema_mismatch%' LIMIT 10").fetchall()
        if not mismatches:
            print("  No schema_mismatch found")
        for m in mismatches:
            print(f"  msg={m[0]} dataset={m[1]} err={str(m[2])[:120]}")
    except Exception as e:
        print(f"  Error: {e}")

    # Check for skipped_rows in table_writes
    print("\n=== Table Write Errors ===")
    try:
        write_errors = c.execute("SELECT table_name, status, error FROM table_writes WHERE error IS NOT NULL AND error != '' LIMIT 10").fetchall()
        if not write_errors:
            print("  No table write errors")
        for w in write_errors:
            print(f"  table={w[0]} status={w[1]} err={str(w[2])[:120]}")
    except Exception as e:
        print(f"  Error: {e}")

    conn.close()


if __name__ == "__main__":
    main()
