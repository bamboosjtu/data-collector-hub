"""Wait for 6 smoke jobs to reach terminal state and report results."""
import json, time
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"
TERMINAL = {"succeeded", "partial", "failed", "cancelled"}

job_ids = [
    "ing_refresh_annual_plans_current_cb080dae9e28",
    "ing_refresh_plan_progress_de8e6436f3ab",
    "ing_refresh_dept_key_personnel_39230c4e554e",
    "ing_refresh_substations_for_project_aa22feac7786",
    "ing_refresh_daily_meetings_by_range_3d90c71f7b04",
    "ing_refresh_daily_meeting_snapshot_8111435b9a94",
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
print("SMOKE RESULTS (Beijing Time)")
print("=" * 80)

all_ok = True
for jid in job_ids:
    job = api(f"/ingestion/v1/jobs/{jid}")
    status = job.get("status", "?")
    error = job.get("error")
    row_count = job.get("row_count", 0) or 0
    trigger = job.get("trigger_key", "?")
    created_at = job.get("created_at", "?")
    icon = "OK" if status == "succeeded" else "!!"
    print(f"  [{icon}] {trigger}: status={status} rows={row_count} created_at={created_at}")
    if error:
        print(f"       error: {error[:100]}")
    if status != "succeeded":
        all_ok = False

print()
print("ALL SUCCEEDED" if all_ok else "SOME FAILED")

# Verify timestamps are Beijing time (UTC+8)
print("\n--- Timestamp Verification ---")
for jid in job_ids:
    job = api(f"/ingestion/v1/jobs/{jid}")
    created = job.get("created_at", "")
    started = job.get("started_at", "")
    print(f"  {job.get('trigger_key','?')}: created_at={created} started_at={started}")
