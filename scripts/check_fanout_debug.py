"""Check dcp_plan_projects row count and fan-out details."""
import json
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Check dcp_plan_projects count
try:
    result = api("/query/v1/dcp_plan_projects?limit=5")
    items = result.get("items", result.get("rows", []))
    print(f"dcp_plan_projects rows: {len(items)} (sample)")
    for r in items[:3]:
        print(f"  prjCode={r.get('prjCode','?')} year={r.get('year','?')}")
except Exception as e:
    print(f"Error querying dcp_plan_projects: {e}")

# Check the parent job result_json in detail
parent_id = "ing_refresh_substations_for_current_plan_projects_3d590db5a1f7"
parent = api(f"/ingestion/v1/jobs/{parent_id}")
print(f"\nParent status: {parent.get('status')}")
print(f"Parent error: {parent.get('error')}")

# Check all children
children_data = api(f"/ingestion/v1/jobs/{parent_id}/children")
children = children_data.get("items", [])
print(f"\nChildren count: {len(children)}")
for c in children:
    params = json.loads(c.get("params_json") or "{}")
    print(f"  {c['ingestion_job_id']} status={c['status']} projectCode={params.get('projectCode','?')} row_count={c.get('row_count',0)}")

# Check the latest jobs to see if there are more substation children
data = api("/ingestion/v1/jobs?limit=30")
sub_jobs = [r for r in data.get("items", []) if r.get("trigger_key") == "refresh_substations_for_project"]
print(f"\nLatest substation child jobs: {len(sub_jobs)}")
for j in sub_jobs[:10]:
    params = json.loads(j.get("params_json") or "{}")
    parent = j.get("parent_job_id", "?")
    print(f"  {j['ingestion_job_id']} status={j['status']} projectCode={params.get('projectCode','?')} parent={parent}")
