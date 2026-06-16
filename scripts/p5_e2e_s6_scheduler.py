"""Section 6: Real Scheduler Trigger Test."""
import sqlite3
import json
import requests
import time
from datetime import datetime, timedelta

DB = "data/datahub_mvp.db"
BASE = "http://localhost:8000"

# Check health
r = requests.get(f"{BASE}/health/ready")
health = r.json()
print(f"Health: scheduler_enabled={health.get('scheduler_enabled')} daily_dcp_refresh_enabled={health.get('daily_dcp_refresh_enabled')}")
print(f"  status={health.get('status')} db={health.get('db')} tables={health.get('tables')}")

# Check current plan state
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
plans = conn.execute("SELECT plan_name, enabled, schedule_type, next_run_at FROM scheduled_plans").fetchall()
for p in plans:
    print(f"  {p['plan_name']}: enabled={p['enabled']} type={p['schedule_type']} next={p['next_run_at']}")

# Ensure dcp_daily_update is enabled with past next_run_at
past_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
conn.execute("UPDATE scheduled_plans SET enabled=1, next_run_at=? WHERE plan_name='dcp_daily_update'", (past_time,))
conn.commit()

# Ensure daily_dcp_refresh is disabled
conn.execute("UPDATE scheduled_plans SET enabled=0 WHERE plan_name='daily_dcp_refresh'")
conn.commit()

# Ensure dcp_initial_full_load is disabled
conn.execute("UPDATE scheduled_plans SET enabled=0 WHERE plan_name='dcp_initial_full_load'")
conn.commit()
conn.close()

print(f"\nSet dcp_daily_update: enabled=1, next_run_at={past_time}")
print("Set daily_dcp_refresh: enabled=0")
print("Set dcp_initial_full_load: enabled=0")

# Wait for scheduler to trigger (scheduler_tick runs every 60s by default)
print("\nWaiting for scheduler to trigger (checking every 15s, up to 120s)...")
for i in range(8):
    time.sleep(15)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # Check for scheduler-triggered runs
    scheduler_runs = conn.execute(
        "SELECT run_id, plan_name, trigger_source, status, started_at FROM scheduled_runs "
        "WHERE plan_name='dcp_daily_update' AND trigger_source='scheduler' ORDER BY started_at DESC LIMIT 3"
    ).fetchall()
    conn.close()

    if scheduler_runs:
        print(f"\n  Scheduler-triggered run found after {(i+1)*15}s!")
        for r in scheduler_runs:
            print(f"    {r['run_id']} | {r['status']} | {r['started_at']}")
        break
    else:
        print(f"  {(i+1)*15}s: No scheduler run yet...")

# Final check
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Check plan state after scheduler
plan = conn.execute("SELECT * FROM scheduled_plans WHERE plan_name='dcp_daily_update'").fetchone()
print(f"\nFinal dcp_daily_update state:")
print(f"  enabled={plan['enabled']} next_run_at={plan['next_run_at']}")

# Check if next_run_at advanced
if plan['next_run_at']:
    next_dt = datetime.strptime(plan['next_run_at'], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    if next_dt > now:
        print(f"  PASS: next_run_at advanced to future ({plan['next_run_at']})")
    else:
        print(f"  WARN: next_run_at still in past ({plan['next_run_at']})")

# Check for scheduler-triggered ingestion_jobs
scheduler_jobs = conn.execute(
    "SELECT ingestion_job_id, trigger_key, source, status FROM ingestion_jobs WHERE source='scheduler' LIMIT 10"
).fetchall()
print(f"\nScheduler-triggered ingestion jobs: {len(scheduler_jobs)}")
for j in scheduler_jobs:
    print(f"  {j['ingestion_job_id'][:40]} | {j['trigger_key']} | {j['source']} | {j['status']}")

# Verify no initial full load was triggered
init_runs = conn.execute(
    "SELECT run_id FROM scheduled_runs WHERE plan_name='dcp_initial_full_load' AND trigger_source='scheduler'"
).fetchall()
print(f"\nScheduler-triggered initial_full_load runs: {len(init_runs)} (should be 0)")

# Verify no 2024-01-01 backfill was triggered by scheduler
scheduler_backfill = conn.execute(
    "SELECT run_id, params_json FROM scheduled_run_steps "
    "WHERE command_name='backfill_daily_meetings_by_range' "
    "AND run_id IN (SELECT run_id FROM scheduled_runs WHERE trigger_source='scheduler')"
).fetchall()
for s in scheduler_backfill:
    params = json.loads(s['params_json'])
    print(f"  Scheduler backfill params: {params}")
    if params.get('startDate') == '2024-01-01':
        print("  ERROR: Scheduler triggered 2024-01-01 full backfill!")
    else:
        print(f"  PASS: No 2024-01-01 backfill from scheduler")

conn.close()
