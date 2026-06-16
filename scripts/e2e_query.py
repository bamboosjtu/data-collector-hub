"""P5 E2E query helper - correct API paths."""
import sys
import requests
import json

BASE = "http://localhost:8000"

def get_json(path, **params):
    r = requests.get(f"{BASE}{path}", params=params)
    r.raise_for_status()
    return r.json()

def post_json(path, **kwargs):
    r = requests.post(f"{BASE}{path}", **kwargs)
    return r.status_code, r.json()

def cmd_steps(run_id):
    """Steps are embedded in run detail."""
    data = get_json(f"/admin/schedules/runs/{run_id}")
    steps = data.get("steps", [])
    print(f"\n=== Steps for {run_id} ===")
    print(f"  Run status: {data.get('status')}")
    print(f"  Started: {data.get('started_at')}  Finished: {data.get('finished_at')}")
    for s in (steps if isinstance(steps, list) else []):
        job_id = s.get("ingestion_job_id", "")
        print(f"  step {s['step_index']}: {s['step_name']} | status={s['status']} | job={job_id}")

def cmd_fanout(job_id):
    data = get_json(f"/ingestion/v1/jobs/{job_id}/fanout")
    summary = data.get("summary", {})
    items = data.get("items", [])
    print(f"\n=== Fanout for {job_id} ===")
    print(f"  Summary: status={summary.get('status')} total={summary.get('total')} "
          f"succeeded={summary.get('succeeded')} failed={summary.get('failed')} "
          f"skipped={summary.get('skipped')} error={summary.get('error')}")
    by_status = {}
    for item in items:
        st = item.get("status", "unknown")
        by_status.setdefault(st, []).append(item)
    for st, group in sorted(by_status.items()):
        print(f"  {st}: {len(group)} items")
        for item in group[:5]:
            code = item.get("project_code", item.get("param_value", ""))
            child_job = item.get("child_job_id", "")
            child_status = item.get("child_status", "")
            print(f"    - {code} -> {child_job[:40]}... {child_status}")
        if len(group) > 5:
            print(f"    ... and {len(group)-5} more")

def cmd_plans():
    data = get_json("/admin/schedules/plans")
    plans = data if isinstance(data, list) else data.get("plans", data.get("items", []))
    print("\n=== Scheduled Plans ===")
    for p in (plans if isinstance(plans, list) else []):
        config = json.loads(p.get("config_json", "{}"))
        print(f"  {p['plan_name']}: enabled={p.get('enabled')} schedule_type={p.get('schedule_type')} "
              f"schedule_time={p.get('schedule_time')} next_run_at={p.get('next_run_at')} "
              f"timeout={config.get('wait_timeout_seconds','N/A')}")

def cmd_jobs(status=None, source=None, limit=50):
    params = {"limit": limit}
    if status:
        params["status"] = status
    if source:
        params["source"] = source
    data = get_json("/ingestion/v1/jobs", **params)
    jobs = data if isinstance(data, list) else data.get("jobs", data.get("items", []))
    print(f"\n=== Jobs (status={status}, source={source}) ===")
    for j in (jobs if isinstance(jobs, list) else []):
        jid = j.get("ingestion_job_id", "")
        print(f"  {jid[:50]} | {j.get('command','')} | {j.get('status','')} | {j.get('source','')} | {str(j.get('error',''))[:60]}")

def cmd_row_counts():
    """Use query routes from plugin.yaml."""
    routes = [
        ("/api/v1/plan/projects", "dcp_plan_year_project"),
        ("/api/v1/project/towers", "dcp_project_tower"),
        ("/api/v1/project/substations", "dcp_project_substation"),
        ("/api/v1/project/line-sections", "dcp_project_line_sections"),
        ("/api/v1/safety/daily-meetings", "dcp_safe_daily_meeting"),
    ]
    print("\n=== Row Counts ===")
    for path, table in routes:
        try:
            data = get_json(path, limit=1)
            total = data.get("total", "N/A")
            print(f"  {table}: {total}")
        except Exception as e:
            print(f"  {table}: ERROR {e}")

def cmd_exceptions():
    """Check for core exceptions."""
    print("\n=== Core Exception Check ===")
    data = get_json("/ingestion/v1/jobs", status="failed", limit=200)
    jobs = data if isinstance(data, list) else data.get("jobs", data.get("items", []))
    schema_mismatch = 0
    callback_auth = 0
    db_locked = 0
    no_connector = 0
    wait_timeout = 0
    unknown = 0
    datahub_bug = 0
    for j in (jobs if isinstance(jobs, list) else []):
        err = (j.get("error") or "").lower()
        cmd = j.get("command", "")
        if "schema" in err and "mismatch" in err:
            schema_mismatch += 1
        elif "401" in err or "403" in err:
            if "0401" not in cmd and "0403" not in cmd:
                callback_auth += 1
        elif "database is locked" in err:
            db_locked += 1
        elif "no connector" in err or "no_connector" in err:
            no_connector += 1
        elif "timeout" in err and ("wait" in err or "exceeded" in err):
            wait_timeout += 1
        elif "datahub" in err or "internal" in err:
            datahub_bug += 1
        else:
            unknown += 1
    print(f"  schema_mismatch: {schema_mismatch}")
    print(f"  callback_401_403: {callback_auth}")
    print(f"  database_locked: {db_locked}")
    print(f"  no_connector: {no_connector}")
    print(f"  wait_timeout: {wait_timeout}")
    print(f"  datahub_bug: {datahub_bug}")
    print(f"  unknown_failed: {unknown}")

    data2 = get_json("/ingestion/v1/jobs", status="partial", limit=200)
    jobs2 = data2 if isinstance(data2, list) else data2.get("jobs", data2.get("items", []))
    print(f"  partial_jobs_count: {len(jobs2) if isinstance(jobs2, list) else 'N/A'}")

def cmd_run_now(plan_name):
    status_code, data = post_json(f"/admin/schedules/plans/{plan_name}/run")
    print(f"\n=== Run Now: {plan_name} ===")
    print(f"  HTTP {status_code}")
    print(f"  Response: {json.dumps(data, indent=2, default=str)}")
    return data

def cmd_update_plan(plan_name, **fields):
    status_code, data = post_json(f"/admin/schedules/plans/{plan_name}", json=fields)
    print(f"\n=== Update Plan: {plan_name} ===")
    print(f"  HTTP {status_code}")
    print(f"  Response: {json.dumps(data, indent=2, default=str)}")
    return data

def cmd_retry_failed(job_id):
    status_code, data = post_json(f"/ingestion/v1/jobs/{job_id}/retry-failed-children")
    print(f"\n=== Retry Failed Children: {job_id} ===")
    print(f"  HTTP {status_code}")
    print(f"  Response: {json.dumps(data, indent=2, default=str)}")

def cmd_db_query(sql):
    """Direct DB query for data not available via API."""
    import sqlite3
    conn = sqlite3.connect("data/datahub_mvp.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchall()
    for r in rows:
        print(dict(r))
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/e2e_query.py <cmd> [args...]")
        print("Commands: steps <run_id> | fanout <job_id> | plans | jobs [status] [source] | rows | exceptions | run_now <plan> | update_plan <plan> <json> | retry <job_id> | db <sql>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "steps":
        cmd_steps(sys.argv[2])
    elif cmd == "fanout":
        cmd_fanout(sys.argv[2])
    elif cmd == "plans":
        cmd_plans()
    elif cmd == "jobs":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        source = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_jobs(status=status, source=source)
    elif cmd == "rows":
        cmd_row_counts()
    elif cmd == "exceptions":
        cmd_exceptions()
    elif cmd == "run_now":
        cmd_run_now(sys.argv[2])
    elif cmd == "update_plan":
        plan_name = sys.argv[2]
        fields = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        cmd_update_plan(plan_name, **fields)
    elif cmd == "retry":
        cmd_retry_failed(sys.argv[2])
    elif cmd == "db":
        cmd_db_query(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
