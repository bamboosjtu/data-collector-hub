"""Check substation fan-out status and find a failed projectCode for retry."""
from urllib.request import Request, urlopen
import json

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Get all jobs
data = api("/ingestion/v1/jobs?limit=200")
items = data.get("items", [])

# Count by command
cmds = {}
for r in items:
    cmd = r.get("trigger_key", "?")
    cmds[cmd] = cmds.get(cmd, 0) + 1

print("=== Job counts by command ===")
for k, v in sorted(cmds.items(), key=lambda x: -x[1]):
    print(f"  {v:4d} {k}")

# Find substation fan-out parent
sub_parents = [r for r in items if "substation" in r.get("trigger_key", "") and "current_plan" in r.get("trigger_key", "")]
print(f"\n=== Substation fan-out parents: {len(sub_parents)} ===")
for p in sub_parents[:3]:
    print(f"  {p['ingestion_job_id']} status={p['status']}")

# Find failed substation children
sub_children = [r for r in items if r.get("trigger_key") == "refresh_substations_for_project"]
print(f"\n=== Substation children: {len(sub_children)} ===")

# Get first few failed substation children with their projectCode
failed_subs = [r for r in sub_children if r["status"] == "failed"]
print(f"  Failed: {len(failed_subs)}")

if failed_subs:
    print("\n=== First 5 failed substation children ===")
    for c in failed_subs[:5]:
        params = json.loads(c.get("params_json") or "{}")
        pc = params.get("projectCode", "?")
        err = (c.get("error") or "")[:80]
        print(f"  {pc} error={err}")
