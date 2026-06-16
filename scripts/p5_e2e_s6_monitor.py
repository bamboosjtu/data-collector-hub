"""Monitor scheduler-triggered run until terminal."""
import sqlite3
import json
import time
from datetime import datetime

DB = "data/datahub_mvp.db"

run_id = "run_dcp_daily_update_e082ac70949a"
print(f"Monitoring {run_id}...")

for i in range(60):  # Check every 30s for up to 30 minutes
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    run = conn.execute("SELECT status, started_at, finished_at FROM scheduled_runs WHERE run_id=?", (run_id,)).fetchone()
    if not run:
        print(f"  Run not found!")
        conn.close()
        break

    status = run["status"]
    if status in ("succeeded", "partial", "failed", "cancelled", "skipped"):
        print(f"\n  Run terminal: {status}")
        print(f"  Started: {run['started_at']}  Finished: {run['finished_at']}")

        # Get steps
        steps = conn.execute(
            "SELECT step_order, command_name, status, job_id FROM scheduled_run_steps WHERE run_id=? ORDER BY step_order",
            (run_id,)
        ).fetchall()
        for s in steps:
            print(f"    step {s['step_order']}: {s['command_name']} | {s['status']}")

        # Check next_run_at
        plan = conn.execute("SELECT next_run_at FROM scheduled_plans WHERE plan_name='dcp_daily_update'").fetchone()
        print(f"\n  dcp_daily_update next_run_at: {plan['next_run_at']}")

        if plan['next_run_at']:
            next_dt = datetime.strptime(plan['next_run_at'], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            if next_dt > now:
                print(f"  PASS: next_run_at advanced to future")
            else:
                print(f"  WARN: next_run_at still in past")

        # Verify trigger_source
        run_full = conn.execute("SELECT trigger_source FROM scheduled_runs WHERE run_id=?", (run_id,)).fetchone()
        print(f"  trigger_source: {run_full['trigger_source']}")

        # Verify no initial full load
        init_runs = conn.execute(
            "SELECT COUNT(*) as cnt FROM scheduled_runs WHERE plan_name='dcp_initial_full_load' AND trigger_source='scheduler'"
        ).fetchone()
        print(f"  scheduler-triggered initial_full_load: {init_runs['cnt']} (should be 0)")

        # Verify ingestion_jobs source
        scheduler_jobs = conn.execute(
            "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE source='scheduler' AND ingestion_job_id IN "
            "(SELECT job_id FROM scheduled_run_steps WHERE run_id=?)",
            (run_id,)
        ).fetchone()
        print(f"  scheduler-source ingestion jobs in this run: {scheduler_jobs['cnt']}")

        conn.close()
        break

    conn.close()
    if i % 4 == 0:
        print(f"  {i*30}s: status={status}")
    time.sleep(30)
else:
    print("Timeout waiting for run to complete!")
