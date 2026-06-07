"""DataHub ops CLI — minimal command-line interface for daily operations.

Usage:
    uv run python -m src.datahub.cli trigger <command> [--params key=val ...]
    uv run python -m src.datahub.cli jobs [--limit N]
    uv run python -m src.datahub.cli job <job_id>
    uv run python -m src.datahub.cli children <job_id>
    uv run python -m src.datahub.cli retry <job_id>
    uv run python -m src.datahub.cli tables
    uv run python -m src.datahub.cli commands
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError


DEFAULT_BASE = "http://localhost:8000"
DEFAULT_KEY = "dev-admin-key"


def _api(method: str, path: str, *, body: dict | None = None, base: str = DEFAULT_BASE, key: str = DEFAULT_KEY) -> dict:
    url = f"{base}{path}"
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, method=method)
    req.add_header("X-API-Key", key)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        detail = e.read().decode()
        try:
            detail = json.loads(detail)
        except Exception:
            pass
        print(f"HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)


def _fmt_time(s: str | None) -> str:
    if not s:
        return "-"
    return s.replace("T", " ")[:19]


def _status_icon(s: str) -> str:
    m = {"succeeded": "OK", "accepted": "OK", "running": "..", "triggering": "..", "partial": "~ ", "failed": "!!", "conflict": "!!"}
    return m.get(s, "?? ")


def cmd_commands(args):
    data = _api("GET", "/plugins", base=args.base, key=args.key)
    for plugin in data.get("items", []):
        for cmd in plugin.get("commands", []):
            if not cmd.get("enabled"):
                continue
            params = ", ".join(cmd.get("required_params", [])) or "-"
            print(f"  {cmd['name']:45s} {cmd.get('trigger_type','?'):18s} params={params}")


def cmd_trigger(args):
    params = {}
    for p in (args.params or []):
        k, _, v = p.partition("=")
        params[k] = v
    result = _api("POST", "/ingestion/v1/jobs", body={"command": args.command, "params": params}, base=args.base, key=args.key)
    print(f"Job created: {result.get('ingestion_job_id', '?')}")
    print(f"Status:      {result.get('status', '?')}")
    if result.get("downloader_job_id"):
        print(f"Producer:    {result['downloader_job_id']}")


def cmd_jobs(args):
    data = _api("GET", f"/ingestion/v1/jobs?limit={args.limit}", base=args.base, key=args.key)
    items = data.get("items", [])
    if not items:
        print("No jobs found.")
        return
    print(f"{'Status':5s} {'Command':40s} {'Job ID':35s} {'Created':20s}")
    print("-" * 105)
    for j in items:
        print(f"{_status_icon(j.get('status','')):5s} {(j.get('trigger_key') or '-'):40s} {j.get('ingestion_job_id',''):35s} {_fmt_time(j.get('created_at')):20s}")


def cmd_job(args):
    j = _api("GET", f"/ingestion/v1/jobs/{args.job_id}", base=args.base, key=args.key)
    print(f"Job ID:     {j.get('ingestion_job_id')}")
    print(f"Parent:     {j.get('parent_job_id') or '-'}")
    print(f"Command:    {j.get('trigger_key')}")
    print(f"Status:     {j.get('status')}")
    print(f"Params:     {j.get('params_json')}")
    print(f"Error:      {j.get('error') or '-'}")
    print(f"Created:    {_fmt_time(j.get('created_at'))}")
    print(f"Finished:   {_fmt_time(j.get('finished_at'))}")
    if j.get("result_json"):
        print(f"Result:     {j['result_json']}")


def cmd_children(args):
    data = _api("GET", f"/ingestion/v1/jobs/{args.job_id}/children", base=args.base, key=args.key)
    items = data.get("items", [])
    total = data.get("total", 0)
    print(f"Parent: {args.job_id}  Children: {total}")
    if not items:
        return
    success = sum(1 for c in items if c.get("status") in ("succeeded", "accepted"))
    failed = sum(1 for c in items if c.get("status") == "failed")
    print(f"Summary: {success} succeeded, {failed} failed, {total - success - failed} other")
    print()
    print(f"{'Status':5s} {'Command':40s} {'Job ID':35s} {'Error':30s}")
    print("-" * 115)
    for c in items:
        err = (c.get("error") or "-")[:30]
        print(f"{_status_icon(c.get('status','')):5s} {(c.get('trigger_key') or '-'):40s} {c.get('ingestion_job_id',''):35s} {err:30s}")


def cmd_retry(args):
    result = _api("POST", f"/ingestion/v1/jobs/{args.job_id}/retry", base=args.base, key=args.key)
    print(f"Retry job created: {result.get('ingestion_job_id', '?')}")
    print(f"Status:            {result.get('status', '?')}")


def cmd_tables(args):
    schemas = _api("GET", "/schemas", base=args.base, key=args.key)
    tables = schemas.get("tables", {})
    print(f"{'Table':40s} {'PK':30s} {'Mode':15s} {'Rows':>8s}  {'Last Updated':20s}")
    print("-" * 120)
    for name in sorted(tables):
        spec = tables[name]
        pk = ", ".join(spec.get("primary_key", []))
        mode = spec.get("write_mode", "?")
        try:
            stats = _api("GET", f"/api/v1/ops/table-stats?table={name}", base=args.base, key=args.key)
            rows = stats.get("row_count", "?")
            updated = _fmt_time(stats.get("last_updated"))
        except Exception:
            rows = "?"
            updated = "-"
        print(f"{name:40s} {pk:30s} {mode:15s} {str(rows):>8s}  {updated:20s}")


def main():
    parser = argparse.ArgumentParser(prog="datahub-cli", description="DataHub ops CLI")
    parser.add_argument("--base", default=DEFAULT_BASE, help=f"Hub base URL (default: {DEFAULT_BASE})")
    parser.add_argument("--key", default=DEFAULT_KEY, help="API key (default: dev-admin-key)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_commands = sub.add_parser("commands", help="List available commands")
    p_commands.set_defaults(func=cmd_commands)

    p_trigger = sub.add_parser("trigger", help="Trigger a command")
    p_trigger.add_argument("command", help="Command name")
    p_trigger.add_argument("--params", nargs="*", help="key=value params (space-separated, e.g. --params max_items=5 cooldown=3)")
    p_trigger.set_defaults(func=cmd_trigger)

    p_jobs = sub.add_parser("jobs", help="List ingestion jobs")
    p_jobs.add_argument("--limit", type=int, default=50)
    p_jobs.set_defaults(func=cmd_jobs)

    p_job = sub.add_parser("job", help="Show job detail")
    p_job.add_argument("job_id")
    p_job.set_defaults(func=cmd_job)

    p_children = sub.add_parser("children", help="List child jobs")
    p_children.add_argument("job_id")
    p_children.set_defaults(func=cmd_children)

    p_retry = sub.add_parser("retry", help="Retry a failed job")
    p_retry.add_argument("job_id")
    p_retry.set_defaults(func=cmd_retry)

    p_tables = sub.add_parser("tables", help="Show table row counts")
    p_tables.set_defaults(func=cmd_tables)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
