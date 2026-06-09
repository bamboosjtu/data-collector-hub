"""Wait for multiple jobs to reach terminal state and report results."""
import json, time, sys
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"
TERMINAL = {"succeeded", "partial", "failed", "cancelled"}

job_ids = [
    "ing_refresh_annual_plans_current_44c428cb2c10",
    "ing_refresh_plan_progress_bf4feb16ec2d",
    "ing_refresh_dept_key_personnel_d24ccf1c5129",
    "ing_refresh_substations_for_project_7c5b05c0ded8",
    "ing_refresh_daily_meetings_by_range_56a56fcea4c1",
    "ing_refresh_daily_meeting_snapshot_78d2fee207ed",
]

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Wait for all to reach terminal
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

# Report results
print("=" * 80)
print("FINAL SMOKE RESULTS")
print("=" * 80)

all_ok = True
for jid in job_ids:
    try:
        job = api(f"/ingestion/v1/jobs/{jid}")
        status = job.get("status", "?")
        error = job.get("error")
        row_count = job.get("row_count", 0) or 0
        trigger = job.get("trigger_key", "?")
        icon = "OK" if status == "succeeded" else "!!"
        print(f"  [{icon}] {trigger}: status={status} row_count={row_count}")
        if error:
            print(f"       error: {error[:100]}")
        if status != "succeeded":
            all_ok = False
    except Exception as e:
        print(f"  [??] {jid}: ERROR - {e}")
        all_ok = False

print()
print("ALL SUCCEEDED" if all_ok else "SOME FAILED")
