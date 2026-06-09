"""Sequential daily meeting verification: snapshot, yesterday, 3-day range, 14-day backfill."""
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


def wait_job(job_id, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{INGESTION}/jobs/{job_id}")
        if r.status_code == 200:
            d = r.json()
            if d.get("status") in ("succeeded", "failed", "partial"):
                return d
        time.sleep(3)
    return None


def trigger(command, params=None, cwd=None):
    cmd = ["uv", "run", "python", "-m", "src.datahub.cli", "trigger", command]
    if params:
        for k, v in params.items():
            cmd.extend(["--params", f"{k}={v}"])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    for line in result.stdout.split("\n"):
        if "Job created:" in line:
            return line.split("Job created:")[1].strip()
    print(f"  TRIGGER ERROR: {result.stderr.strip()[:200]}")
    return None


def check_table(table_name, db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(f"select count(*) from {table_name}")
    count = c.fetchone()[0]

    c.execute(f"select count(*) from {table_name} where prjName is not null")
    prj_name_count = c.fetchone()[0]
    c.execute(f"select count(*) from {table_name} where biddingSectionCode is not null")
    bs_count = c.fetchone()[0]
    c.execute(f"select count(*) from {table_name} where singleProjectCode is not null")
    sp_count = c.fetchone()[0]
    c.execute(f"select count(*) from {table_name} where leaderName is not null")
    leader_count = c.fetchone()[0]

    c.execute(f"select extra from {table_name} limit 5")
    extra_sizes = []
    for r in c.fetchall():
        if r["extra"]:
            extra = json.loads(r["extra"])
            extra_sizes.append(len(extra))

    c.execute(f"select extra from {table_name} limit 10")
    forbidden = {"raw", "payload", "response", "result"}
    has_forbidden = False
    for r in c.fetchall():
        if r["extra"]:
            extra = json.loads(r["extra"])
            if forbidden & set(extra.keys()):
                has_forbidden = True
                break

    c.execute(
        f"select date, id, prjName, biddingSectionCode, singleProjectCode, leaderName, workSiteName "
        f"from {table_name} limit 3"
    )
    samples = c.fetchall()

    conn.close()
    return {
        "count": count,
        "prjName_count": prj_name_count,
        "biddingSectionCode_count": bs_count,
        "singleProjectCode_count": sp_count,
        "leaderName_count": leader_count,
        "extra_avg_keys": sum(extra_sizes) / len(extra_sizes) if extra_sizes else 0,
        "has_forbidden_extra": has_forbidden,
        "samples": [dict(zip(["date", "id", "prjName", "biddingSectionCode", "singleProjectCode", "leaderName", "workSiteName"], r)) for r in samples],
    }


def main():
    from src.datahub.core.time_utils import datahub_today, datahub_days_ago

    parser = argparse.ArgumentParser(description="Daily meeting full verification")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path")
    parser.add_argument("--cwd", default=DEFAULT_CWD, help="DataHub project root")
    args = parser.parse_args()

    today = datahub_today()
    yesterday = datahub_days_ago(1)
    range_start = datahub_days_ago(3)
    backfill_start = datahub_days_ago(14)

    print(flush=True)

    # Step 1: refresh_daily_meeting_snapshot
    print("[1] refresh_daily_meeting_snapshot...", end=" ", flush=True)
    job_id = trigger("refresh_daily_meeting_snapshot", cwd=args.cwd)
    if not job_id:
        print("TRIGGER FAILED"); sys.exit(1)
    result = wait_job(job_id, timeout=120)
    if not result:
        print("TIMEOUT"); sys.exit(1)
    print(result["status"], flush=True)

    info = check_table("dcp_daily_meeting_snapshot", args.db)
    print(f"  rows={info['count']}  prjName={info['prjName_count']}  biddingSectionCode={info['biddingSectionCode_count']}  singleProjectCode={info['singleProjectCode_count']}  leaderName={info['leaderCount']}", flush=True)
    print(f"  extra_avg_keys={info['extra_avg_keys']:.1f}  forbidden_extra={info['has_forbidden_extra']}", flush=True)
    for s in info["samples"]:
        print(f"  sample: {s}", flush=True)

    # Step 2: refresh_daily_meetings_yesterday
    print(f"\n[2] refresh_daily_meetings_yesterday...", end=" ", flush=True)
    job_id = trigger("refresh_daily_meetings_yesterday", cwd=args.cwd)
    if not job_id:
        print("TRIGGER FAILED"); sys.exit(1)
    result = wait_job(job_id, timeout=120)
    if not result:
        print("TIMEOUT"); sys.exit(1)
    print(result["status"], flush=True)

    info = check_table("dcp_daily_meeting", args.db)
    print(f"  rows={info['count']}  prjName={info['prjName_count']}  biddingSectionCode={info['biddingSectionCode_count']}  singleProjectCode={info['singleProjectCode_count']}  leaderName={info['leader_count']}", flush=True)
    print(f"  extra_avg_keys={info['extra_avg_keys']:.1f}  forbidden_extra={info['has_forbidden_extra']}", flush=True)

    # Step 3: refresh_daily_meetings_by_range (3 days)
    print(f"\n[3] refresh_daily_meetings_by_range (3 days)...", end=" ", flush=True)
    job_id = trigger("refresh_daily_meetings_by_range", {"startDate": str(range_start), "endDate": str(today)}, cwd=args.cwd)
    if not job_id:
        print("TRIGGER FAILED"); sys.exit(1)
    result = wait_job(job_id, timeout=120)
    if not result:
        print("TIMEOUT"); sys.exit(1)
    print(result["status"], flush=True)

    info = check_table("dcp_daily_meeting", args.db)
    print(f"  rows={info['count']}  prjName={info['prjName_count']}  biddingSectionCode={info['biddingSectionCode_count']}  singleProjectCode={info['singleProjectCode_count']}  leaderName={info['leader_count']}", flush=True)
    print(f"  extra_avg_keys={info['extra_avg_keys']:.1f}  forbidden_extra={info['has_forbidden_extra']}", flush=True)

    # Step 4: backfill_daily_meetings_by_range (14 days)
    print(f"\n[4] backfill_daily_meetings_by_range (14 days)...", flush=True)
    job_id = trigger("backfill_daily_meetings_by_range", {
        "startDate": str(backfill_start), "endDate": str(today),
        "chunk_days": "1", "cooldown_seconds": "3",
    }, cwd=args.cwd)
    if not job_id:
        print("TRIGGER FAILED"); sys.exit(1)

    start = time.time()
    while time.time() - start < 600:
        r = requests.get(f"{INGESTION}/jobs/{job_id}")
        if r.status_code == 200:
            d = r.json()
            if d.get("status") in ("succeeded", "failed", "partial"):
                print(f"  {d['status']} ({int(time.time()-start)}s)", flush=True)
                break
        time.sleep(5)

    info = check_table("dcp_daily_meeting", args.db)
    print(f"  rows={info['count']}  prjName={info['prjName_count']}  biddingSectionCode={info['biddingSectionCode_count']}  singleProjectCode={info['singleProjectCode_count']}  leaderName={info['leader_count']}", flush=True)
    print(f"  extra_avg_keys={info['extra_avg_keys']:.1f}  forbidden_extra={info['has_forbidden_extra']}", flush=True)

    # Final verification
    print(f"\n{'='*60}", flush=True)
    print("ACCEPTANCE CHECK", flush=True)
    print(f"{'='*60}", flush=True)

    r = requests.get(f"{HUB}/api/v1/safety/daily-meetings", params={"date": str(yesterday), "limit": 5})
    if r.status_code == 200:
        data = r.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        print(f"  PASS: query route /api/v1/safety/daily-meetings?date={yesterday} returned {len(items) if isinstance(items, list) else '?'} items", flush=True)
    else:
        print(f"  FAIL: query route returned {r.status_code}", flush=True)

    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    c.execute("select date, id, prjName, biddingSectionCode, singleProjectCode, leaderName, workSiteName from dcp_daily_meeting limit 5")
    for r in c.fetchall():
        print(f"  SQL: {r}", flush=True)

    c.execute("select count(*) from dcp_daily_meeting where extra is not null and extra != 'null' and extra != '{}'")
    extra_count = c.fetchone()[0]
    c.execute("select count(*) from dcp_daily_meeting")
    total = c.fetchone()[0]
    print(f"\n  extra populated: {extra_count}/{total}", flush=True)

    conn.close()


if __name__ == "__main__":
    main()
