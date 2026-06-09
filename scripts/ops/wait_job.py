"""Wait for a job to reach terminal state and print result."""
import time, json, sys
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"
KEY = "dev-admin-key"
TERMINAL = {"succeeded", "partial", "failed", "cancelled"}

job_id = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: wait_job.py <job_id>")

for _ in range(60):  # max 5 min
    req = Request(f"{BASE}/ingestion/v1/jobs/{job_id}")
    req.add_header("X-API-Key", KEY)
    data = json.loads(urlopen(req).read().decode())
    status = data.get("status", "")
    if status in TERMINAL:
        print(f"status={status}")
        print(f"error={data.get('error') or 'none'}")
        print(f"row_count={data.get('row_count', 0)}")
        print(f"message_received={data.get('message_received', 0)}")
        result = data.get("result_json")
        if result:
            print(f"result_json={result[:200]}")
        sys.exit(0)
    time.sleep(5)

print("TIMEOUT waiting for job to reach terminal state")
