"""P1 online integration helper - query DB for smoke test verification."""
import sqlite3
import json
import sys

DB = "data/datahub_mvp.db"

def query(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return result

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "help"

    if action == "last_run":
        run_id = sys.argv[2] if len(sys.argv) > 2 else None
        if run_id:
            rows = query("select run_id, plan_name, trigger_source, status, error, started_at, finished_at from scheduled_runs where run_id=?", (run_id,))
        else:
            rows = query("select run_id, plan_name, trigger_source, status, error, started_at, finished_at from scheduled_runs order by started_at desc limit 5")
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))

    elif action == "steps":
        run_id = sys.argv[2]
        rows = query("select id, step_order, command_name, status, error, job_id, wait_for_terminal from scheduled_run_steps where run_id=? order by step_order", (run_id,))
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))

    elif action == "jobs":
        run_id = sys.argv[2]
        rows = query("""
            select ij.ingestion_job_id, ij.trigger_key, ij.source, ij.status, ij.error, ij.params_json, ij.producer_status_json
            from ingestion_jobs ij
            where ij.ingestion_job_id in (
                select s.job_id from scheduled_run_steps s where s.run_id=? and s.job_id is not null
            )
            order by ij.id
        """, (run_id,))
        for r in rows:
            # Truncate long JSON fields for readability
            if r.get("params_json") and len(r["params_json"]) > 200:
                r["params_json"] = r["params_json"][:200] + "..."
            if r.get("producer_status_json") and len(r["producer_status_json"]) > 200:
                r["producer_status_json"] = r["producer_status_json"][:200] + "..."
            print(json.dumps(r, ensure_ascii=False))

    elif action == "plan":
        plan_name = sys.argv[2]
        rows = query("select plan_name, enabled, schedule_type, schedule_time, next_run_at, last_run_id, last_status from scheduled_plans where plan_name=?", (plan_name,))
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))

    elif action == "anomalies":
        # Check for schema_mismatch, callback errors, database locked, no_connector
        rows = query("""
            select ingestion_job_id, trigger_key, status, error
            from ingestion_jobs
            where status='failed'
            and created_at > datetime('now', '-1 hour')
            order by id desc limit 20
        """)
        if rows:
            print("FAILED JOBS (last hour):")
            for r in rows:
                print(json.dumps(r, ensure_ascii=False))
        else:
            print("NO FAILED JOBS in last hour")

        # Check for callback errors in ingestion_messages
        rows2 = query("""
            select message_id, status, error
            from ingestion_messages
            where status='failed'
            and created_at > datetime('now', '-1 hour')
            order by id desc limit 10
        """)
        if rows2:
            print("FAILED MESSAGES (last hour):")
            for r in rows2:
                print(json.dumps(r, ensure_ascii=False))
        else:
            print("NO FAILED MESSAGES in last hour")

    elif action == "all_plans":
        rows = query("select plan_name, enabled, schedule_type, schedule_time, next_run_at, last_run_id, last_status from scheduled_plans")
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))

    else:
        print("Usage: python scripts/p1_online.py <action> [args]")
        print("Actions: last_run [run_id], steps <run_id>, jobs <run_id>, plan <plan_name>, anomalies, all_plans")

if __name__ == "__main__":
    main()
