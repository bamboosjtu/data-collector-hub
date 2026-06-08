"""Find the earliest available date for daily meeting data."""
import sqlite3
import urllib.request
import json

# Test specific dates to find the boundary
test_dates = [
    "2025-12-08", "2025-12-15", "2025-12-22", "2025-12-29",
    "2026-01-05", "2026-01-12", "2026-01-19", "2026-01-26",
    "2026-02-02", "2026-02-09", "2026-02-16", "2026-02-23",
    "2026-03-01", "2026-03-05", "2026-03-08", "2026-03-09",
]

for date in test_dates:
    try:
        payload = json.dumps({
            "job_type": "safe_daily_meeting_range",
            "params": {"startDate": date, "endDate": date},
            "sink": {
                "type": "http_callback",
                "url": "http://localhost:8000/ingestion/v1/table-batches",
                "headers": {"X-Callback-Key": "dev-default-callback-key"}
            }
        }).encode()
        req = urllib.request.Request(
            "http://localhost:8010/sync",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        dl_job_id = data.get("downloader_job_id", "?")
        print(f"Date {date}: job_id={dl_job_id}")
    except Exception as e:
        print(f"Date {date}: ERROR - {e}")
