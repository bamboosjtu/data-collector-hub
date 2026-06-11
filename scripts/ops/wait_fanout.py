"""Wait for a fan-out parent job to reach terminal state, then print a local report."""
import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "datahub_mvp.db"
TERMINAL = {"succeeded", "partial", "failed", "cancelled"}


def api_get(base_url: str, api_key: str, path: str) -> dict:
    req = Request(f"{base_url.rstrip('/')}{path}")
    req.add_header("X-API-Key", api_key)
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_table_counts(db_path: Path) -> dict:
    tables = ["dcp_project_tower", "dcp_project_substation", "dcp_project_line_sections", "dcp_project_line_branches"]
    counts = {}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        for table in tables:
            c.execute(f'SELECT COUNT(*) FROM "{table}"')
            counts[table] = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM dcp_project_substation "
            "WHERE id IS NULL AND prjCode IS NULL "
            "AND longitude IS NULL AND latitude IS NULL "
            "AND longitudeLook IS NULL AND latitudeLook IS NULL"
        )
        counts["dcp_project_substation_empty_shells"] = c.fetchone()[0]
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for a fan-out parent job and print child/table status")
    parser.add_argument("parent_job_id", help="Fan-out parent ingestion job id")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path")
    parser.add_argument("--base-url", default="http://localhost:8000", help="DataHub API base URL")
    parser.add_argument("--api-key", default="dev-admin-key", help="DataHub API key")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout seconds")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return 1

    print(f"Waiting for {args.parent_job_id}...", flush=True)
    start = time.time()
    status = ""
    while time.time() - start < args.timeout:
        data = api_get(args.base_url, args.api_key, f"/ingestion/v1/jobs/{args.parent_job_id}")
        status = data.get("status", "?")
        elapsed = int(time.time() - start)
        if elapsed % 60 < 5:
            print(f"  [{elapsed}s] status={status}", flush=True)
        if status in TERMINAL:
            break
        time.sleep(5)
    else:
        print(f"TIMEOUT after {args.timeout}s waiting for terminal state")
        return 1

    duration = int(time.time() - start)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        parent = c.execute(
            "SELECT * FROM ingestion_jobs WHERE ingestion_job_id = ?",
            (args.parent_job_id,),
        ).fetchone()
        if not parent:
            print(f"Parent job not found in DB: {args.parent_job_id}")
            return 1

        print(f"\n{'=' * 60}", flush=True)
        print(f"RESULT: {parent['status']} (duration: {duration}s / {duration // 60}m{duration % 60}s)", flush=True)
        print(f"{'=' * 60}", flush=True)

        rows = c.execute(
            "SELECT status, COUNT(*) FROM ingestion_jobs "
            "WHERE parent_job_id = ? GROUP BY status",
            (args.parent_job_id,),
        ).fetchall()
        total = 0
        print("\nChildren:", flush=True)
        for row in rows:
            print(f"  {row[0]}: {row[1]}", flush=True)
            total += row[1]
        print(f"  total: {total}", flush=True)

        failed = c.execute(
            "SELECT ingestion_job_id, status, error, params_json FROM ingestion_jobs "
            "WHERE parent_job_id = ? AND status IN ('failed','partial')",
            (args.parent_job_id,),
        ).fetchall()
        if failed:
            print(f"\nFailed children ({len(failed)}):", flush=True)
            for row in failed:
                error = (row["error"] or "")[:120]
                params = (row["params_json"] or "")[:80]
                print(f"  {row['status']} {row['ingestion_job_id']} params={params} error={error}", flush=True)

    counts = get_table_counts(db_path)
    print("\nTable counts:", flush=True)
    for table in ["dcp_project_tower", "dcp_project_substation", "dcp_project_line_sections", "dcp_project_line_branches"]:
        print(f"  {table}: {counts.get(table, '?')}", flush=True)
    print(f"  dcp_project_substation empty_shells: {counts.get('dcp_project_substation_empty_shells', '?')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())