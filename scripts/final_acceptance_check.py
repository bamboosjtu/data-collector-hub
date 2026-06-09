"""Final acceptance check for MVP seal."""
import json
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

print("=" * 80)
print("MVP FINAL ACCEPTANCE CHECK")
print("=" * 80)

# 1. Check ingestion_messages for all smoke jobs
job_ids = [
    "ing_refresh_annual_plans_current_44c428cb2c10",
    "ing_refresh_plan_progress_bf4feb16ec2d",
    "ing_refresh_dept_key_personnel_d24ccf1c5129",
    "ing_refresh_substations_for_project_7c5b05c0ded8",
    "ing_refresh_daily_meetings_by_range_56a56fcea4c1",
    "ing_refresh_daily_meeting_snapshot_78d2fee207ed",
]

print("\n--- 1. Job Status ---")
for jid in job_ids:
    job = api(f"/ingestion/v1/jobs/{jid}")
    status = job.get("status")
    error = job.get("error")
    row_count = job.get("row_count", 0) or 0
    trigger = job.get("trigger_key", "?")
    icon = "OK" if status == "succeeded" else "!!"
    print(f"  [{icon}] {trigger}: status={status} rows={row_count} error={error or 'none'}")

# 2. Check for schema_mismatch across all recent jobs
print("\n--- 2. Error Checks ---")
data = api("/ingestion/v1/jobs?limit=50")
items = data.get("items", [])

schema_mismatch = sum(1 for r in items if r.get("error") and "schema_mismatch" in str(r.get("error", "")))
callback_auth = sum(1 for r in items if r.get("error") and ("401" in str(r.get("error", "")) or "403" in str(r.get("error", ""))))
db_locked = sum(1 for r in items if r.get("error") and "database locked" in str(r.get("error", "")).lower())
disk_io = sum(1 for r in items if r.get("error") and "disk i/o" in str(r.get("error", "")).lower())

print(f"  schema_mismatch: {schema_mismatch}")
print(f"  callback 401/403: {callback_auth}")
print(f"  database locked: {db_locked}")
print(f"  disk I/O error: {disk_io}")

# 3. Check dcp_substation empty wrapper rows
print("\n--- 3. Data Quality ---")
try:
    sub_result = api("/api/v1/project/substations?limit=500")
    sub_items = sub_result.get("items", [])
    empty_wrapper = sum(1 for r in sub_items if not r.get("singleProjectCode") and not r.get("substationName"))
    print(f"  dcp_substation: {len(sub_items)} rows, empty_wrapper={empty_wrapper}")
except Exception as e:
    print(f"  dcp_substation: ERROR - {e}")

# 4. Check dcp_daily_meeting extra is not null
try:
    dm_result = api("/api/v1/safety/daily-meetings?limit=500")
    dm_items = dm_result.get("items", [])
    extra_not_null = sum(1 for r in dm_items if r.get("extra") is not None)
    print(f"  dcp_daily_meeting: {len(dm_items)} sample rows, extra NOT NULL={extra_not_null}")
except Exception as e:
    print(f"  dcp_daily_meeting: ERROR - {e}")

# 5. Check dcp_daily_meeting_snapshot
try:
    snap_result = api("/api/v1/safety/daily-meeting-snapshots?limit=10")
    snap_items = snap_result.get("items", [])
    print(f"  dcp_daily_meeting_snapshot: {len(snap_items)} sample rows")
except Exception as e:
    print(f"  dcp_daily_meeting_snapshot: ERROR - {e}")

# 6. Business tables row counts
print("\n--- 4. Business Tables ---")
tables_to_check = [
    ("dcp_plan_projects", "/api/v1/plan/projects?limit=1"),
    ("dcp_plan_progress", "/api/v1/plan/progress?limit=1"),
    ("dcp_dept_key_personnel", "/api/v1/dept/personnel?limit=1"),
    ("dcp_substation", "/api/v1/project/substations?limit=1"),
    ("dcp_daily_meeting", "/api/v1/safety/daily-meetings?limit=1"),
    ("dcp_daily_meeting_snapshot", "/api/v1/safety/daily-meeting-snapshots?limit=1"),
]
for table_name, path in tables_to_check:
    try:
        result = api(path)
        total = result.get("total", len(result.get("items", [])))
        print(f"  {table_name}: {total} rows")
    except Exception as e:
        print(f"  {table_name}: ERROR - {str(e)[:60]}")

print("\n" + "=" * 80)
print("ACCEPTANCE CHECK COMPLETE")
print("=" * 80)
