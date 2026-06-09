"""Check fan-out parent and children details."""
import json, sys
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

parent_id = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: check_fanout_detail.py <parent_id>")

# Parent details
parent = api(f"/ingestion/v1/jobs/{parent_id}")
print("=== PARENT ===")
print(f"  status: {parent.get('status')}")
print(f"  error: {parent.get('error')}")
print(f"  trigger_key: {parent.get('trigger_key')}")
rj = parent.get("result_json")
if rj:
    print(f"  result_json: {rj[:1000]}")

# Children
children_data = api(f"/ingestion/v1/jobs/{parent_id}/children")
children = children_data.get("items", [])
print(f"\n=== CHILDREN: {len(children)} ===")
for c in children:
    params = json.loads(c.get("params_json") or "{}")
    print(f"  {c['ingestion_job_id']} status={c['status']} projectCode={params.get('projectCode','?')} error={str(c.get('error',''))[:60]}")
