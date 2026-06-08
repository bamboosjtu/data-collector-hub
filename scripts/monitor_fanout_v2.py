"""Monitor fan-out parent and its children."""
import time, json, sys
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"
TERMINAL = {"succeeded", "partial", "failed", "cancelled"}

parent_id = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: monitor_fanout.py <parent_job_id>")

def api(path):
    req = Request(f"{BASE}{path}")
    req.add_header("X-API-Key", KEY)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())

for attempt in range(120):  # max 10 min
    parent = api(f"/ingestion/v1/jobs/{parent_id}")
    status = parent.get("status", "")

    # Get children
    children_data = api(f"/ingestion/v1/jobs/{parent_id}/children")
    children = children_data.get("items", [])

    by_status = {}
    for c in children:
        s = c.get("status", "?")
        by_status[s] = by_status.get(s, 0) + 1

    result_preview = ""
    result_json = parent.get("result_json")
    if result_json:
        try:
            rj = json.loads(result_json) if isinstance(result_json, str) else result_json
            result_preview = f" created={rj.get('created_children','?')} succ={rj.get('succeeded_children','?')} fail={rj.get('failed_children','?')} skipped={rj.get('skipped_remaining_projects','?')}"
        except Exception:
            pass

    print(f"[{attempt+1}] parent={status} children={len(children)} {by_status}{result_preview}")

    if status in TERMINAL:
        print(f"\n=== FINAL ===")
        print(f"status={status}")
        print(f"error={parent.get('error') or 'none'}")
        if result_json:
            print(f"result_json={result_json[:500]}")
        sys.exit(0)

    time.sleep(5)

print("TIMEOUT")
