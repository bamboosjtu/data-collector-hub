"""Final acceptance check for project fan-out circuit breaker."""
import json
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

parent_id = "ing_refresh_substations_for_current_plan_projects_863dd6090ec8"

# 1. Check parent
parent = api(f"/ingestion/v1/jobs/{parent_id}")
print("=== PARENT ===")
print(f"  status: {parent.get('status')}")
print(f"  error: {parent.get('error')}")

# 2. Check children
children_data = api(f"/ingestion/v1/jobs/{parent_id}/children")
children = children_data.get("items", [])
print(f"\n=== CHILDREN: {len(children)} ===")

by_status = {}
for c in children:
    s = c.get("status", "?")
    by_status[s] = by_status.get(s, 0) + 1
print(f"  By status: {by_status}")

# 3. Check child params - should NOT contain fan-out control params
bad_params = []
for c in children:
    params = json.loads(c.get("params_json") or "{}")
    for key in ("max_items", "max_concurrency", "cooldown_seconds", "consecutive_failure_threshold"):
        if key in params:
            bad_params.append((c["ingestion_job_id"], key))
if bad_params:
    print(f"\n  !! BAD CHILD PARAMS: {bad_params}")
else:
    print(f"\n  Child params clean: no fan-out control params found")

# 4. Check for schema_mismatch in errors
schema_mismatch = [c for c in children if c.get("error") and "schema_mismatch" in str(c.get("error", ""))]
print(f"\n  schema_mismatch errors: {len(schema_mismatch)}")

# 5. Check for callback 401/403
auth_errors = [c for c in children if c.get("error") and ("401" in str(c.get("error", "")) or "403" in str(c.get("error", "")))]
print(f"  callback 401/403 errors: {len(auth_errors)}")

# 6. Check for database locked
db_locked = [c for c in children if c.get("error") and "database locked" in str(c.get("error", "")).lower()]
print(f"  database locked errors: {len(db_locked)}")

# 7. Check for disk I/O error
disk_io = [c for c in children if c.get("error") and "disk i/o" in str(c.get("error", "")).lower()]
print(f"  disk I/O errors: {len(disk_io)}")

# 8. Check row_counts
row_counts = [c.get("row_count", 0) or 0 for c in children]
print(f"\n  row_count: total={sum(row_counts)}, min={min(row_counts)}, max={max(row_counts)}")
zero_row_succeeded = [c for c in children if c.get("status") == "succeeded" and (c.get("row_count") or 0) == 0]
print(f"  succeeded with row_count=0: {len(zero_row_succeeded)} (projects with no substations)")

# 9. Check ingestion_messages for this parent's children
print("\n=== SUMMARY ===")
print(f"  Parent status: {parent.get('status')}")
print(f"  Children total: {len(children)}")
print(f"  Children succeeded: {by_status.get('succeeded', 0)}")
print(f"  Children failed: {by_status.get('failed', 0)}")
print(f"  Circuit breaker triggered: {'YES' if 'circuit breaker' in str(parent.get('error', '')) else 'NO'}")
print(f"  schema_mismatch: {len(schema_mismatch)}")
print(f"  callback 401/403: {len(auth_errors)}")
print(f"  database locked: {len(db_locked)}")
print(f"  disk I/O error: {len(disk_io)}")
print(f"  child params clean: {'YES' if not bad_params else 'NO'}")

# 10. Verify dcp_substation data
try:
    sub_result = api("/query/v1/dcp_substation?limit=1")
    sub_items = sub_result.get("items", sub_result.get("rows", []))
    print(f"  dcp_substation queryable: YES ({len(sub_items)} sample rows)")
except Exception as e:
    print(f"  dcp_substation queryable: ERROR - {e}")
