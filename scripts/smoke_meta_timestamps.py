"""Wait for 6 smoke jobs and verify _ingest_created_at/updated_at."""
import json, time
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"
TERMINAL = {"succeeded", "partial", "failed", "cancelled"}

job_ids = [
    "ing_refresh_annual_plans_current_ce6078acf69f",
    "ing_refresh_plan_progress_225798718528",
    "ing_refresh_dept_key_personnel_6dd555c12293",
    "ing_refresh_substations_for_project_01881cc1377c",
    "ing_refresh_daily_meetings_by_range_c90366a7ddfd",
    "ing_refresh_daily_meeting_snapshot_c498579810ea",
]

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

for attempt in range(60):
    all_terminal = True
    for jid in job_ids:
        try:
            job = api(f"/ingestion/v1/jobs/{jid}")
            if job.get("status") not in TERMINAL:
                all_terminal = False
                break
        except Exception:
            all_terminal = False
            break
    if all_terminal:
        break
    time.sleep(5)

print("=" * 80)
print("SMOKE RESULTS")
print("=" * 80)

for jid in job_ids:
    job = api(f"/ingestion/v1/jobs/{jid}")
    status = job.get("status", "?")
    row_count = job.get("row_count", 0) or 0
    trigger = job.get("trigger_key", "?")
    icon = "OK" if status == "succeeded" else ("~" if status == "partial" else "!!")
    print(f"  [{icon}] {trigger}: status={status} rows={row_count}")

# Check business table _ingest_created_at / _ingest_updated_at
print("\n--- Business Table Meta Timestamps ---")
import sqlite3
conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row

for table_name in ["dcp_plan_projects", "dcp_substation", "dcp_daily_meeting"]:
    try:
        row = conn.execute(f"SELECT _ingest_created_at, _ingest_updated_at FROM {table_name} LIMIT 1").fetchone()
        if row:
            created = row["_ingest_created_at"]
            updated = row["_ingest_updated_at"]
            print(f"  {table_name}: created_at={created} updated_at={updated}")
            if created is None:
                print(f"    !! _ingest_created_at is NULL")
            if updated is None:
                print(f"    !! _ingest_updated_at is NULL")
        else:
            print(f"  {table_name}: no rows")
    except Exception as e:
        print(f"  {table_name}: {e}")

conn.close()
