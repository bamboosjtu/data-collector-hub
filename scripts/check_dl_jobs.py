"""Check downloader job status for 180-day backfill children."""
import sqlite3
import urllib.request
import json

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

parent_id = "ing_backfill_daily_meetings_by_range_d0ef0c42b0bd"

# Get all child downloader_job_ids
cur.execute("SELECT ingestion_job_id, downloader_job_id, params_json FROM ingestion_jobs WHERE parent_job_id=? LIMIT 10", (parent_id,))
rows = cur.fetchall()

for r in rows:
    dl_job_id = r["downloader_job_id"]
    params = json.loads(r["params_json"])
    try:
        req = urllib.request.Request(f"http://localhost:8010/sync/jobs/{dl_job_id}")
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        status = data.get("status", "?")
        error = None
        for c in data.get("collects", []):
            if c.get("error"):
                error = c["error"]
                break
        print(f"Date: {params.get('startDate', '?')}, DL status: {status}, error: {error}")
    except Exception as e:
        print(f"Date: {params.get('startDate', '?')}, DL job: {dl_job_id}, Error: {e}")

conn.close()
