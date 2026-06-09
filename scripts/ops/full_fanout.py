"""Full fan-out verification script.
Runs one fan-out command, waits for terminal state, records all metrics.
"""
import argparse
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import requests

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "datahub_mvp.db"
DEFAULT_CWD = str(Path(__file__).resolve().parents[2])

HUB = "http://localhost:8000"
INGESTION = f"{HUB}/ingestion/v1"


def get_table_counts(db_path) -> dict:
    counts = {}
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for t in ["dcp_tower", "dcp_substation", "dcp_line_sections", "dcp_line_branches"]:
        c.execute(f"select count(*) from {t}")
        counts[t] = c.fetchone()[0]
    c.execute(
        "select count(*) from dcp_substation "
        "where id is null and prjCode is null "
        "and longitude is null and latitude is null "
        "and longitudeLook is null and latitudeLook is null"
    )
    counts["dcp_substation_empty_shells"] = c.fetchone()[0]
    conn.close()
    return counts


def trigger_fanout(command: str, cwd: str) -> str | None:
    cmd = [
        "uv", "run", "python", "-m", "src.datahub.cli", "trigger", command,
        "--params", "max_concurrency=1", "cooldown_seconds=5",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    for line in result.stdout.split("\n"):
        if "Job created:" in line:
            return line.split("Job created:")[1].strip()
    if result.returncode != 0:
        print(f"  TRIGGER ERROR: {result.stderr.strip()[:200]}")
    return None


def wait_for_job(job_id: str, timeout=3600) -> dict | None:
    start = time.time()
    last_print = 0
    while time.time() - start < timeout:
        r = requests.get(f"{INGESTION}/jobs/{job_id}")
        if r.status_code != 200:
            time.sleep(5)
            continue
        d = r.json()
        status = d.get("status", "?")
        elapsed = int(time.time() - start)
        if elapsed - last_print >= 60:
            print(f"    [{elapsed}s] status={status}")
            last_print = elapsed
        if status in ("succeeded", "failed", "partial"):
            return d
        time.sleep(5)
    return None


def get_children_stats(parent_id: str) -> dict:
    r = requests.get(f"{INGESTION}/jobs/{parent_id}/children")
    d = r.json()
    items = d if isinstance(d, list) else d.get("items", [])
    from collections import Counter
    c = Counter(j.get("status") for j in items)
    return {"total": len(items), "by_status": dict(c)}


def get_failed_children(parent_id: str) -> list:
    r = requests.get(f"{INGESTION}/jobs/{parent_id}/children")
    d = r.json()
    items = d if isinstance(d, list) else d.get("items", [])
    failed = [j for j in items if j.get("status") in ("failed", "partial")]
    return [{
        "job_id": j.get("ingestion_job_id", "?")[:70],
        "status": j.get("status"),
        "error": (j.get("error") or "")[:150],
        "params": (j.get("params_json") or "")[:80],
    } for j in failed]


def main():
    parser = argparse.ArgumentParser(description="Run full fan-out and verify")
    parser.add_argument("command", help="Fan-out command to trigger")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path")
    parser.add_argument("--cwd", default=DEFAULT_CWD, help="DataHub project root")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"FULL FAN-OUT: {args.command}")
    print(f"{'='*60}")

    counts_before = get_table_counts(args.db)
    print(f"\nBefore: {json.dumps(counts_before)}")

    start_time = time.time()
    job_id = trigger_fanout(args.command, args.cwd)
    if not job_id:
        print("TRIGGER FAILED - STOPPING")
        sys.exit(1)

    print(f"Parent job: {job_id}")
    print("Waiting for terminal state (timeout=60min)...")

    result = wait_for_job(job_id, timeout=3600)
    duration = int(time.time() - start_time)

    if not result:
        print(f"TIMEOUT after {duration}s - STOPPING")
        sys.exit(1)

    parent_status = result.get("status")
    parent_error = result.get("error", "")

    print(f"\n{'='*60}")
    print(f"RESULT: {parent_status} (duration: {duration}s / {duration//60}m{duration%60}s)")
    print(f"{'='*60}")

    children = get_children_stats(job_id)
    print(f"Children: {json.dumps(children)}")

    failed_children = get_failed_children(job_id)
    if failed_children:
        print(f"\nFailed children ({len(failed_children)}):")
        for fc in failed_children[:10]:
            print(f"  {fc['status']}: {fc['params']} - {fc['error']}")

    counts_after = get_table_counts(args.db)
    print(f"\nTable counts:")
    for t in ["dcp_tower", "dcp_substation", "dcp_line_sections", "dcp_line_branches"]:
        delta = counts_after.get(t, 0) - counts_before.get(t, 0)
        print(f"  {t}: {counts_before.get(t, 0)} -> {counts_after.get(t, 0)} (delta=+{delta})")

    print(f"  dcp_substation empty_shells: {counts_after.get('dcp_substation_empty_shells', '?')}")

    # Stop condition checks
    print(f"\n{'='*60}")
    print("STOP CONDITION CHECKS:")
    print(f"{'='*60}")
    stop = False
    checks = [
        ("schema_mismatch", "schema_mismatch" not in parent_error),
        ("callback 401/403", "401" not in parent_error and "403" not in parent_error),
        ("disk I/O error", "disk I/O" not in parent_error.lower()),
        ("dcp_substation empty_shells=0", counts_after.get("dcp_substation_empty_shells", -1) == 0),
        ("child failed <= 5", children["by_status"].get("failed", 0) <= 5),
    ]
    for name, passed in checks:
        status = "PASS" if passed else "STOP"
        print(f"  {status}: {name}")
        if not passed:
            stop = True

    if stop:
        print("\n*** STOP CONDITION TRIGGERED - DO NOT PROCEED ***")
        sys.exit(1)
    else:
        print("\nAll checks passed - safe to proceed to next fan-out")


if __name__ == "__main__":
    main()
