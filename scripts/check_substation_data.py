"""Quick check dcp_substation data via query API."""
import json
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Query substations
result = api("/api/v1/project/substations?limit=100")
items = result.get("items", [])
total = result.get("total", len(items))
print(f"dcp_substation total: {total}")
print(f"Sample rows: {len(items)}")

# Check for empty wrapper rows (all fields null except API fields)
empty_count = 0
for r in items:
    spc = r.get("singleProjectCode")
    name = r.get("substationName")
    if not spc and not name:
        empty_count += 1

print(f"Empty wrapper rows: {empty_count}")

# Show first few
for r in items[:5]:
    print(f"  projectCode={r.get('singleProjectCode','?')} name={r.get('substationName','?')} type={r.get('substationType','?')}")
