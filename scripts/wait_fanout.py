"""Wait for a fan-out parent job to reach terminal state, then print full report."""
import requests
import time
import json
import sqlite3
import sys

HUB = "http://localhost:8000"
INGESTION = f"{HUB}/ingestion/v1"


def get_table_counts() -> dict:
    counts = {}
    conn = sqlite3.connect("data/datahub_mvp.db")
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wait_fanout.py <parent_job_id>")
        sys.exit(1)

    parent_id = sys.argv[1]
    print(f"Waiting for {parent_id}...", flush=True)

    start = time.time()
    while True:
        r = requests.get(f"{INGESTION}/jobs/{parent_id}")
        if r.status_code == 200:
            d = r.json()
            status = d.get("status", "?")
            elapsed = int(time.time() - start)
            if elapsed % 60 < 6:
                print(f"  [{elapsed}s] status={status}", flush=True)
            if status in ("succeeded", "failed", "partial"):
                break
        time.sleep(5)

    duration = int(time.time() - start)

    # Full report
    conn = sqlite3.connect("data/datahub_mvp.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("select * from ingestion_jobs where ingestion_job_id = ?", (parent_id,))
    parent = c.fetchone()

    print(f"\n{'='*60}", flush=True)
    print(f"RESULT: {parent['status']} (duration: {duration}s / {duration//60}m{duration%60}s)", flush=True)
    print(f"{'='*60}", flush=True)

    # Children stats
    c.execute(
        "select status, count(*) from ingestion_jobs "
        "where parent_job_id = ? group by status",
        (parent_id,),
    )
    children = c.fetchall()
    total = 0
    print(f"\nChildren:", flush=True)
    for r in children:
        print(f"  {r[0]}: {r[1]}", flush=True)
        total += r[1]
    print(f"  total: {total}", flush=True)

    # Failed children
    c.execute(
        "select ingestion_job_id, status, error, params_json from ingestion_jobs "
        "where parent_job_id = ? and status in ('failed','partial')",
        (parent_id,),
    )
    failed = c.fetchall()
    if failed:
        print(f"\nFailed children ({len(failed)}):", flush=True)
        for r in failed:
            print(f"  {r['params_json'][:60]}  status={r['status']}  error={r['error'][:120]}", flush=True)

    # Table counts
    counts = get_table_counts()
    print(f"\nTable counts:", flush=True)
    for t in ["dcp_tower", "dcp_substation", "dcp_line_sections", "dcp_line_branches"]:
        print(f"  {t}: {counts.get(t, '?')}", flush=True)
    print(f"  dcp_substation empty_shells: {counts.get('dcp_substation_empty_shells', '?')}", flush=True)

    conn.close()
