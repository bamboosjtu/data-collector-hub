"""Check snapshot job details."""
import json
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

job = api("/ingestion/v1/jobs/ing_refresh_daily_meeting_snapshot_8111435b9a94")
print(f"status: {job.get('status')}")
print(f"error: {job.get('error')}")
print(f"row_count: {job.get('row_count', 0)}")
print(f"message_received: {job.get('message_received', 0)}")
print(f"message_total: {job.get('message_total', 0)}")
ps = job.get("producer_status_json", "")
if ps:
    print(f"producer_status: {ps[:300]}")
