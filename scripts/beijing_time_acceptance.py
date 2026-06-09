"""Final acceptance check for Beijing timezone migration."""
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
print("BEIJING TIMEZONE MIGRATION - ACCEPTANCE CHECK")
print("=" * 80)

# 1. Check job timestamps are Beijing time format
job_ids = [
    "ing_refresh_annual_plans_current_cb080dae9e28",
    "ing_refresh_plan_progress_de8e6436f3ab",
    "ing_refresh_dept_key_personnel_39230c4e554e",
    "ing_refresh_substations_for_project_aa22feac7786",
    "ing_refresh_daily_meetings_by_range_3d90c71f7b04",
    "ing_refresh_daily_meeting_snapshot_8111435b9a94",
]

print("\n--- 1. Job Status & Timestamps ---")
all_succeeded = True
for jid in job_ids:
    job = api(f"/ingestion/v1/jobs/{jid}")
    status = job.get("status")
    created = job.get("created_at", "MISSING")
    started = job.get("started_at", "MISSING")
    trigger = job.get("trigger_key", "?")
    icon = "OK" if status == "succeeded" else ("~" if status == "partial" else "!!")
    print(f"  [{icon}] {trigger}: status={status} created_at={created} started_at={started}")
    if status not in ("succeeded", "partial"):
        all_succeeded = False

# 2. Verify timestamps are NOT UTC (should be Beijing time, ~8 hours ahead)
print("\n--- 2. Timestamp Format Verification ---")
from datetime import datetime as dt, timezone
from zoneinfo import ZoneInfo
beijing_now = dt.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
job = api(f"/ingestion/v1/jobs/{job_ids[0]}")
created_at = job.get("created_at", "")
if created_at:
    created_hour = int(created_at.split(" ")[1].split(":")[0])
    utc_hour = dt.now(timezone.utc).hour
    beijing_hour = dt.now(ZoneInfo("Asia/Shanghai")).hour
    print(f"  created_at hour: {created_hour}")
    print(f"  current UTC hour: {utc_hour}")
    print(f"  current Beijing hour: {beijing_hour}")
    if abs(created_hour - beijing_hour) <= 1:
        print(f"  Timestamp is BEIJING TIME (OK)")
    else:
        print(f"  WARNING: Timestamp may not be Beijing time!")

# 3. Check ingestion_messages timestamps
print("\n--- 3. Message Timestamps ---")
messages = api("/ingestion/v1/messages?limit=5")
msg_items = messages.get("items", [])
for m in msg_items[:3]:
    mid = m.get("message_id", "?")[:30]
    received = m.get("received_at", "MISSING")
    created = m.get("created_at", "MISSING")
    print(f"  {mid}: received_at={received} created_at={created}")

# 4. Check table_writes timestamps
print("\n--- 4. Table Write Timestamps ---")
tw = api("/ingestion/v1/table-writes?limit=5")
tw_items = tw.get("items", [])
for t in tw_items[:3]:
    tbl = t.get("table_name", "?")
    started = t.get("started_at", "MISSING")
    finished = t.get("finished_at", "MISSING")
    created = t.get("created_at", "MISSING")
    print(f"  {tbl}: started={started} finished={finished} created={created}")

# 5. Error checks
print("\n--- 5. Error Metrics ---")
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

print("\n" + "=" * 80)
print("ACCEPTANCE CHECK COMPLETE")
print("=" * 80)
