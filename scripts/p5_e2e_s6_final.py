"""Section 6 Final: Verify scheduler-triggered run results."""
import sqlite3
import json
from datetime import datetime

DB = "data/datahub_mvp.db"
run_id = "run_dcp_daily_update_e082ac70949a"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Run info
run = conn.execute("SELECT * FROM scheduled_runs WHERE run_id=?", (run_id,)).fetchone()
print(f"=== Scheduler-Triggered Run: {run_id} ===")
print(f"  status: {run['status']}")
print(f"  trigger_source: {run['trigger_source']}")
print(f"  started_at: {run['started_at']}")
print(f"  finished_at: {run['finished_at']}")

# Duration
try:
    start = datetime.strptime(run['started_at'], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(run['finished_at'], "%Y-%m-%d %H:%M:%S")
    print(f"  duration: {end - start}")
except:
    pass

# Steps
steps = conn.execute(
    "SELECT step_order, command_name, status, job_id, params_json FROM scheduled_run_steps WHERE run_id=? ORDER BY step_order",
    (run_id,)
).fetchall()
print(f"\n  Steps:")
for s in steps:
    print(f"    step {s['step_order']}: {s['command_name']} | {s['status']}")

# Backfill params
backfill = [s for s in steps if "backfill" in s["command_name"]]
if backfill:
    params = json.loads(backfill[0]["params_json"])
    print(f"\n  backfill params: {params}")
    if params.get("startDate") == "2024-01-01":
        print("  ERROR: Scheduler triggered 2024-01-01 backfill!")
    else:
        print("  PASS: No 2024-01-01 backfill from scheduler")

# next_run_at
plan = conn.execute("SELECT next_run_at, enabled FROM scheduled_plans WHERE plan_name='dcp_daily_update'").fetchone()
print(f"\n  dcp_daily_update next_run_at: {plan['next_run_at']} enabled: {plan['enabled']}")
next_dt = datetime.strptime(plan['next_run_at'], "%Y-%m-%d %H:%M:%S")
now = datetime.now()
if next_dt > now:
    print(f"  PASS: next_run_at advanced to future")
else:
    print(f"  WARN: next_run_at still in past")

# No initial full load triggered
init_runs = conn.execute(
    "SELECT COUNT(*) as cnt FROM scheduled_runs WHERE plan_name='dcp_initial_full_load' AND trigger_source='scheduler'"
).fetchone()
print(f"\n  scheduler-triggered initial_full_load: {init_runs['cnt']} (should be 0)")

# daily_dcp_refresh still disabled
legacy = conn.execute("SELECT enabled FROM scheduled_plans WHERE plan_name='daily_dcp_refresh'").fetchone()
print(f"  daily_dcp_refresh enabled: {legacy['enabled']} (should be 0)")

# Ingestion jobs source
scheduler_jobs = conn.execute(
    "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE source='scheduler' AND ingestion_job_id IN "
    "(SELECT job_id FROM scheduled_run_steps WHERE run_id=? AND job_id IS NOT NULL)",
    (run_id,)
).fetchone()
print(f"  scheduler-source ingestion jobs: {scheduler_jobs['cnt']}")

# Verify ingestion_jobs.source for all steps
for s in steps:
    if s["job_id"]:
        job = conn.execute("SELECT source FROM ingestion_jobs WHERE ingestion_job_id=?", (s["job_id"],)).fetchone()
        if job:
            print(f"    step {s['step_order']}: source={job['source']}")

# Fanout details for scheduler run
fanout_parents = [s for s in steps if "current_plan_projects" in s["command_name"]]
print(f"\n  Fanout details:")
for parent in fanout_parents:
    items = conn.execute(
        "SELECT status, COUNT(*) as cnt FROM fanout_items WHERE parent_job_id=? GROUP BY status",
        (parent["job_id"],)
    ).fetchall()
    status_str = ", ".join(f"{r['status']}={r['cnt']}" for r in items)
    print(f"    {parent['command_name']}: {status_str}")

conn.close()
