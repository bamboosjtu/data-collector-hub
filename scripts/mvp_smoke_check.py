"""Lightweight smoke check for DataHub MVP.

Does NOT trigger heavy collection by default.
Pass --run-plan <plan_name> to optionally trigger a scheduled plan run.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "data" / "datahub_mvp.db"

REQUIRED_TABLES = [
    "ingestion_jobs",
    "fanout_runs",
    "fanout_items",
    "scheduled_plans",
    "scheduled_runs",
    "scheduled_run_steps",
]

POLL_INTERVAL = 3
POLL_TIMEOUT = 120


def _get(url: str, headers: dict[str, str] | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return exc.code, body
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)
    except Exception as exc:  # noqa: BLE001
        return 0, str(exc)


def _post(url: str, headers: dict[str, str] | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, data=b"", method="POST")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return exc.code, body
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)
    except Exception as exc:  # noqa: BLE001
        return 0, str(exc)


def check_health(base: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/health")
    if status == 200:
        try:
            data = json.loads(body)
            if data.get("status") == "ok":
                return True, "GET /health returns status ok"
        except json.JSONDecodeError:
            pass
    return False, f"GET /health failed (status={status})"


def check_health_ready(base: str, api_key: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/health/ready", {"X-API-Key": api_key})
    if status == 200:
        try:
            data = json.loads(body)
            if data.get("status") == "ok":
                return True, "GET /health/ready returns status ok"
        except json.JSONDecodeError:
            pass
    return False, f"GET /health/ready failed (status={status})"


def check_plugins(base: str, api_key: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/plugins", {"X-API-Key": api_key})
    if status == 200:
        try:
            data = json.loads(body)
            if data.get("items") and len(data["items"]) > 0:
                return True, f"GET /plugins returns {len(data['items'])} item(s)"
        except json.JSONDecodeError:
            pass
    return False, f"GET /plugins failed (status={status})"


def check_schemas(base: str, api_key: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/schemas", {"X-API-Key": api_key})
    if status == 200:
        try:
            data = json.loads(body)
            if data.get("tables") and len(data["tables"]) > 0:
                return True, f"GET /schemas returns {len(data['tables'])} table(s)"
        except json.JSONDecodeError:
            pass
    return False, f"GET /schemas failed (status={status})"


def check_ingestion_jobs(base: str, api_key: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/ingestion/v1/jobs?limit=5", {"X-API-Key": api_key})
    if status == 200:
        try:
            data = json.loads(body)
            if data.get("items") is not None:
                return True, f"GET /ingestion/v1/jobs?limit=5 returns {len(data['items'])} item(s)"
        except json.JSONDecodeError:
            pass
    return False, f"GET /ingestion/v1/jobs?limit=5 failed (status={status})"


def check_scheduled_plans(base: str, api_key: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/admin/schedules/plans", {"X-API-Key": api_key})
    if status == 200:
        try:
            data = json.loads(body)
            if data.get("items") is not None:
                return True, f"GET /admin/schedules/plans returns {len(data['items'])} item(s)"
        except json.JSONDecodeError:
            pass
    return False, f"GET /admin/schedules/plans failed (status={status})"


def check_ops(base: str) -> tuple[bool, str]:
    status, body = _get(f"{base}/ops")
    if status == 200 and "DataHub Ops" in body:
        return True, "GET /ops returns HTML containing 'DataHub Ops'"
    return False, f"GET /ops failed (status={status})"


def check_sqlite_tables(db_path: str) -> tuple[bool, str]:
    p = Path(db_path)
    if not p.exists():
        return False, f"SQLite DB not found: {db_path}"
    conn = sqlite3.connect(str(p))
    try:
        existing = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        if not missing:
            return True, f"SQLite: all {len(REQUIRED_TABLES)} required tables exist"
        return False, f"SQLite: missing tables: {', '.join(missing)}"
    except Exception as exc:  # noqa: BLE001
        return False, f"SQLite check error: {exc}"
    finally:
        conn.close()


def check_no_alter_table() -> tuple[bool, str]:
    ddl_path = PROJECT_ROOT / "src" / "datahub" / "storage" / "ddl.py"
    if not ddl_path.exists():
        return True, "ddl.py not found (skipped)"
    content = ddl_path.read_text(encoding="utf-8")
    if "ALTER TABLE" in content:
        return False, "ALTER TABLE found in ddl.py - migration functions must not exist"
    return True, "No ALTER TABLE in ddl.py"


def run_plan(base: str, api_key: str, plan_name: str) -> None:
    print(f"\n--- Triggering plan: {plan_name} ---")
    status, body = _post(f"{base}/admin/schedules/plans/{plan_name}/run", {"X-API-Key": api_key})
    if status != 202:
        print(f"[FAIL] POST /admin/schedules/plans/{plan_name}/run returned {status}: {body[:200]}")
        return
    try:
        data = json.loads(body)
        run_id = data.get("run_id")
    except json.JSONDecodeError:
        print(f"[FAIL] Could not parse run response: {body[:200]}")
        return

    if not run_id:
        print(f"[FAIL] No run_id in response: {body[:200]}")
        return

    print(f"  run_id={run_id}, initial_status={data.get('status', '?')}")

    elapsed = 0
    while elapsed < POLL_TIMEOUT:
        status, body = _get(f"{base}/admin/schedules/runs/{run_id}", {"X-API-Key": api_key})
        if status != 200:
            print(f"  [WARN] Poll returned {status}, retrying...")
        else:
            try:
                run_data = json.loads(body)
                run_status = run_data.get("status", "unknown")
                if run_status in ("completed", "failed", "cancelled"):
                    print(f"[OK] Run {run_id} finished: status={run_status}")
                    steps = run_data.get("steps", [])
                    for step in steps:
                        s = step.get("status", "?")
                        cmd = step.get("command_name", "?")
                        print(f"  step {cmd}: {s}")
                    return
            except json.JSONDecodeError:
                print(f"  [WARN] Could not parse poll response")

        import time
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    print(f"[FAIL] Run {run_id} did not reach terminal status within {POLL_TIMEOUT}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="DataHub MVP smoke check")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of DataHub API")
    parser.add_argument("--api-key", default=os.environ.get("DATAHUB_ADMIN_API_KEY", "dev-admin-key"), help="API key (or set DATAHUB_ADMIN_API_KEY env var)")
    parser.add_argument("--run-plan", default=None, metavar="PLAN_NAME", help="Trigger run-now for a scheduled plan and wait for completion")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite DB for table checks")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    api_key = args.api_key

    results: list[tuple[bool, str]] = []

    print("=== DataHub MVP Smoke Check ===\n")

    print("[1/9] Health check...")
    results.append(check_health(base))

    print("[2/9] Health ready check...")
    results.append(check_health_ready(base, api_key))

    print("[3/9] Plugins check...")
    results.append(check_plugins(base, api_key))

    print("[4/9] Schemas check...")
    results.append(check_schemas(base, api_key))

    print("[5/9] Ingestion jobs check...")
    results.append(check_ingestion_jobs(base, api_key))

    print("[6/9] Scheduled plans check...")
    results.append(check_scheduled_plans(base, api_key))

    print("[7/9] Ops page check...")
    results.append(check_ops(base))

    print("[8/9] SQLite tables check...")
    results.append(check_sqlite_tables(args.db))

    print("[9/9] No ALTER TABLE check...")
    results.append(check_no_alter_table())

    print()
    all_ok = True
    for ok, desc in results:
        tag = "OK" if ok else "FAIL"
        print(f"  [{tag}] {desc}")
        if not ok:
            all_ok = False

    if args.run_plan:
        run_plan(base, api_key, args.run_plan)

    print()
    if all_ok:
        print("All checks passed.")
        sys.exit(0)
    else:
        print("Some checks FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
