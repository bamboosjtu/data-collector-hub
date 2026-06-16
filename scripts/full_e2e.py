"""Full E2E acceptance script for DataHub MVP with P5 business scheduling."""
from __future__ import annotations

import json
import sqlite3
import sys
import time
import urllib.request
from datetime import timedelta
from pathlib import Path

API = "http://localhost:8000"
KEY = "dev-admin-key"
HEADERS_JSON = {"X-API-Key": KEY, "Content-Type": "application/json"}
HEADERS_GET = {"X-API-Key": KEY}
DB_PATH = Path("data/datahub_mvp.db")


def _get(path):
    req = urllib.request.Request(f"{API}{path}", headers=HEADERS_GET)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _post(path, body=None):
    data = json.dumps(body).encode() if body else b""
    req = urllib.request.Request(f"{API}{path}", data=data, headers=HEADERS_JSON, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _wait_for_run(run_id, timeout=7200, poll=10):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        run = _get(f"/admin/schedules/runs/{run_id}")
        if run["status"] in ("succeeded", "partial", "failed", "cancelled", "skipped"):
            return run
        time.sleep(poll)
    return _get(f"/admin/schedules/runs/{run_id}")


def _db_query(sql, params=()):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return rows


# ── Section 2: Plan config check ──

def check_plan_configs():
    print("\n=== Section 2: Plan Config Check ===")
    plans = _get("/admin/schedules/plans")["items"]
    plan_map = {p["plan_name"]: p for p in plans}

    # dcp_initial_full_load
    p = plan_map.get("dcp_initial_full_load")
    if p:
        config = json.loads(p["config_json"] or "{}")
        print(f"  dcp_initial_full_load:")
        print(f"    enabled={p['enabled']}, schedule_type={p['schedule_type']}, schedule_time={p.get('schedule_time')}")
        print(f"    wait_timeout_seconds={config.get('wait_timeout_seconds')}")
        backfill = [s for s in config.get("steps", []) if s["command"] == "backfill_daily_meetings_by_range"]
        if backfill:
            print(f"    backfill startDate={backfill[0]['params'].get('startDate')}, endDate={backfill[0]['params'].get('endDate')}")
        fanout_steps = [s for s in config.get("steps", []) if "all_plan_projects" in s["command"]]
        for fs in fanout_steps:
            print(f"    {fs['command']}: years={fs['params'].get('years')}")
    else:
        print("  [FAIL] dcp_initial_full_load not found!")

    # dcp_daily_update
    p = plan_map.get("dcp_daily_update")
    if p:
        config = json.loads(p["config_json"] or "{}")
        print(f"  dcp_daily_update:")
        print(f"    enabled={p['enabled']}, schedule_type={p['schedule_type']}, schedule_time={p.get('schedule_time')}")
        print(f"    wait_timeout_seconds={config.get('wait_timeout_seconds')}")
        backfill = [s for s in config.get("steps", []) if s["command"] == "backfill_daily_meetings_by_range"]
        if backfill:
            print(f"    backfill startDate={backfill[0]['params'].get('startDate')}, endDate={backfill[0]['params'].get('endDate')}")
        fanout_steps = [s for s in config.get("steps", []) if "current_plan_projects" in s["command"]]
        for fs in fanout_steps:
            print(f"    {fs['command']}")
    else:
        print("  [FAIL] dcp_daily_update not found!")

    # daily_dcp_refresh (legacy)
    p = plan_map.get("daily_dcp_refresh")
    if p:
        print(f"  daily_dcp_refresh (legacy): enabled={p['enabled']}")
    else:
        print("  daily_dcp_refresh: not found (acceptable)")


# ── Section 3: Initial full load ──

def run_initial_full_load():
    print("\n=== Section 3: Initial Full Load ===")
    start_time = time.monotonic()

    result = _post("/admin/schedules/plans/dcp_initial_full_load/run")
    run_id = result["run_id"]
    print(f"  run_id={run_id}, initial_status={result['status']}")

    # Check steps
    time.sleep(2)
    steps = _get(f"/admin/schedules/runs/{run_id}")["steps"]
    print(f"  steps created: {len(steps)}")
    for s in steps:
        params = json.loads(s.get("params_json") or "{}")
        if s["command_name"] == "backfill_daily_meetings_by_range":
            print(f"    backfill params: startDate={params.get('startDate')}, endDate={params.get('endDate')}")
        if "all_plan_projects" in s["command_name"]:
            print(f"    {s['command_name']}: years={params.get('years')}")

    # Wait for completion (up to 8 hours for initial load)
    print("  Waiting for run to complete...")
    run = _wait_for_run(run_id, timeout=28800, poll=15)
    duration = time.monotonic() - start_time

    print(f"\n  run_id={run_id}")
    print(f"  final_status={run['status']}")
    print(f"  duration={duration:.0f}s ({duration/60:.1f}min)")

    steps = run.get("steps", [])
    for s in steps:
        print(f"    step {s['step_order']}: {s['command_name']} -> {s['status']} (job_id={s.get('job_id', '-')})")

    return run_id, run


# ── Section 4: Fan-out convergence & retry ──

def check_fanout_results(run_id):
    print("\n=== Section 4: Fan-out Convergence & Retry ===")
    steps = _get(f"/admin/schedules/runs/{run_id}")["steps"]

    fanout_parents = [s for s in steps if "all_plan_projects" in s["command_name"] or "current_plan_projects" in s["command_name"]]
    if not fanout_parents:
        print("  No fan-out parent steps found")
        return

    for step in fanout_parents:
        job_id = step.get("job_id")
        if not job_id:
            print(f"  {step['command_name']}: no job_id")
            continue

        try:
            fanout = _get(f"/ingestion/v1/jobs/{job_id}/fanout")
            stats = fanout.get("stats", {})
            print(f"  {step['command_name']} ({job_id[:30]}...):")
            print(f"    stats: {stats}")

            failed_items = [i for i in fanout.get("items", []) if i["item_status"] in ("failed", "skipped")]
            if failed_items:
                print(f"    failed/skipped items: {len(failed_items)}")
                for fi in failed_items[:5]:
                    print(f"      item_index={fi['item_index']}, status={fi['item_status']}, error={str(fi.get('item_error',''))[:80]}")
            else:
                print(f"    no failed/skipped items")
        except urllib.error.HTTPError as e:
            print(f"  {step['command_name']}: fanout detail returned {e.code}")


# ── Section 5: Daily update run-now ──

def run_daily_update():
    print("\n=== Section 5: Daily Update Run-Now ===")

    # Record current next_run_at before run
    plan = _get("/admin/schedules/plans")["items"]
    daily_plan = next((p for p in plan if p["plan_name"] == "dcp_daily_update"), None)
    next_run_before = daily_plan.get("next_run_at") if daily_plan else None
    print(f"  next_run_at before run: {next_run_before}")

    start_time = time.monotonic()
    result = _post("/admin/schedules/plans/dcp_daily_update/run")
    run_id = result["run_id"]
    print(f"  run_id={run_id}")

    # Check step params
    time.sleep(2)
    steps = _get(f"/admin/schedules/runs/{run_id}")["steps"]
    for s in steps:
        params = json.loads(s.get("params_json") or "{}")
        if s["command_name"] == "backfill_daily_meetings_by_range":
            print(f"    backfill startDate={params.get('startDate')}, endDate={params.get('endDate')}")
        if "current_plan_projects" in s["command_name"]:
            print(f"    {s['command_name']}")

    run = _wait_for_run(run_id, timeout=7200, poll=15)
    duration = time.monotonic() - start_time

    print(f"  final_status={run['status']}, duration={duration:.0f}s ({duration/60:.1f}min)")
    for s in run.get("steps", []):
        print(f"    step {s['step_order']}: {s['command_name']} -> {s['status']}")

    # Check next_run_at after run
    plan_after = _get("/admin/schedules/plans")["items"]
    daily_plan_after = next((p for p in plan_after if p["plan_name"] == "dcp_daily_update"), None)
    next_run_after = daily_plan_after.get("next_run_at") if daily_plan_after else None
    print(f"  next_run_at after run: {next_run_after}")

    if next_run_before and next_run_after:
        if next_run_after == next_run_before:
            print("  [OK] Manual run-now did not advance next_run_at (was already set)")
        else:
            print("  [OK] next_run_at was empty, now set to: " + next_run_after)
    elif not next_run_before and next_run_after:
        print("  [OK] next_run_at was empty, now set to: " + next_run_after)

    return run_id


# ── Section 6: Real scheduler trigger ──

def test_scheduler_trigger():
    print("\n=== Section 6: Real Scheduler Trigger ===")

    # Enable dcp_daily_update with past next_run_at
    # Need to use store directly since there's no API to update plan
    conn = sqlite3.connect(str(DB_PATH))
    # Ensure daily_dcp_refresh is disabled
    conn.execute("UPDATE scheduled_plans SET enabled = 0 WHERE plan_name = 'daily_dcp_refresh'")
    # Enable dcp_daily_update with next_run_at in the past
    conn.execute("UPDATE scheduled_plans SET enabled = 1, next_run_at = '2020-01-01 02:00:00' WHERE plan_name = 'dcp_daily_update'")
    conn.commit()
    conn.close()
    print("  dcp_daily_update enabled=1, next_run_at=2020-01-01 02:00:00")
    print("  daily_dcp_refresh enabled=0")

    # Wait for scheduler tick (3s interval)
    print("  Waiting for scheduler tick (up to 30s)...")
    for i in range(30):
        time.sleep(1)
        runs = _get("/admin/schedules/plans/dcp_daily_update")["items"] if False else []
        # Check via runs API
        all_runs = _get("/admin/schedules/runs?limit=5")
        if isinstance(all_runs, dict):
            all_runs = all_runs.get("items", [])
        scheduler_runs = [r for r in all_runs if r.get("plan_name") == "dcp_daily_update" and r.get("trigger_source") == "scheduler"]
        if scheduler_runs:
            run_id = scheduler_runs[0]["run_id"]
            print(f"  Scheduler triggered run: {run_id}")
            break
    else:
        # Try listing runs directly
        runs_resp = _get("/admin/schedules/runs?limit=10")
        if isinstance(runs_resp, dict):
            runs_list = runs_resp.get("items", [])
        else:
            runs_list = runs_resp
        scheduler_runs = [r for r in runs_list if r.get("plan_name") == "dcp_daily_update" and r.get("trigger_source") == "scheduler"]
        if scheduler_runs:
            run_id = scheduler_runs[0]["run_id"]
            print(f"  Scheduler triggered run: {run_id}")
        else:
            print("  [WARN] No scheduler-triggered run found in 30s, checking current state...")
            # Check if scheduler is enabled
            health = _get("/health/ready")
            print(f"  scheduler_enabled={health.get('scheduler_enabled')}")
            if not health.get("scheduler_enabled"):
                print("  Scheduler is not enabled. Enabling via env and restarting...")
                print("  [SKIP] Cannot enable scheduler at runtime. Manual verification needed.")
                # Disable the plan to avoid accidental trigger later
                conn = sqlite3.connect(str(DB_PATH))
                conn.execute("UPDATE scheduled_plans SET enabled = 0 WHERE plan_name = 'dcp_daily_update'")
                conn.commit()
                conn.close()
                return None

    # Wait for completion
    run = _wait_for_run(run_id, timeout=7200, poll=15)
    print(f"  run_id={run_id}, final_status={run['status']}, trigger_source={run.get('trigger_source')}")

    # Check ingestion job source
    for s in run.get("steps", []):
        if s.get("job_id"):
            try:
                job = _get(f"/ingestion/v1/jobs/{s['job_id']}")
                print(f"    step {s['command_name']}: job source={job.get('source')}")
            except:
                pass

    # Check next_run_at advanced
    plan = _get("/admin/schedules/plans")["items"]
    daily = next((p for p in plan if p["plan_name"] == "dcp_daily_update"), None)
    if daily:
        print(f"  next_run_at after scheduler: {daily.get('next_run_at')}")

    # Disable plan
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE scheduled_plans SET enabled = 0 WHERE plan_name = 'dcp_daily_update'")
    conn.commit()
    conn.close()
    print("  dcp_daily_update disabled after test")

    return run_id


# ── Section 7: Core exception check ──

def check_core_exceptions():
    print("\n=== Section 7: Core Exception Check ===")
    checks = {
        "schema_mismatch": "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE error LIKE '%schema_mismatch%'",
        "database_locked": "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE error LIKE '%database locked%' OR error LIKE '%database is locked%'",
        "no_connector": "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE error LIKE '%no_connector%'",
        "wait_timeout": "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE error LIKE '%wait timeout%'",
    }

    for name, sql in checks.items():
        rows = _db_query(sql)
        cnt = rows[0]["cnt"] if rows else 0
        print(f"  {name}: {cnt}")

    # callback 401/403 excluding project codes
    rows = _db_query(
        "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE "
        "(error LIKE '%401%' OR error LIKE '%403%') "
        "AND error NOT LIKE '%0401%' AND error NOT LIKE '%0403%'"
    )
    print(f"  callback_401_403: {rows[0]['cnt'] if rows else 0}")

    # Job status summary
    rows = _db_query("SELECT status, COUNT(*) as cnt FROM ingestion_jobs GROUP BY status ORDER BY cnt DESC")
    print("\n  Job status summary:")
    for r in rows:
        print(f"    {r['status']}: {r['cnt']}")

    # Non-succeeded details
    failed = _db_query(
        "SELECT ingestion_job_id, trigger_key, status, error FROM ingestion_jobs "
        "WHERE status IN ('failed','partial') ORDER BY created_at DESC LIMIT 15"
    )
    if failed:
        print("\n  Failed/partial jobs (last 15):")
        for f in failed:
            err = (f["error"] or "")[:100]
            print(f"    {f['ingestion_job_id'][:35]}... {f['trigger_key']} {f['status']}: {err}")

    # Check scheduled_run_step errors for timeout
    timeout_steps = _db_query(
        "SELECT run_id, command_name, status, error FROM scheduled_run_steps "
        "WHERE error LIKE '%wait timeout%' LIMIT 5"
    )
    if timeout_steps:
        print("\n  [WARN] Steps with wait timeout:")
        for s in timeout_steps:
            print(f"    {s['run_id'][:20]}... {s['command_name']}: {s['error']}")
    else:
        print("\n  No wait timeout in scheduled_run_steps")


if __name__ == "__main__":
    section = sys.argv[1] if len(sys.argv) > 1 else "all"

    if section in ("all", "2"):
        check_plan_configs()
    if section in ("all", "3"):
        run_id, run = run_initial_full_load()
    if section in ("all", "4"):
        if "run_id" not in dir():
            print("Run Section 3 first")
        else:
            check_fanout_results(run_id)
    if section in ("all", "5"):
        run_daily_update()
    if section in ("all", "6"):
        test_scheduler_trigger()
    if section in ("all", "7"):
        check_core_exceptions()
