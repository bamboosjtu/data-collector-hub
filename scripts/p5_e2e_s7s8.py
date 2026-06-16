"""P5 E2E - Sections 7-8: Core exception check and row counts."""
import sqlite3
import json

DB = "data/datahub_mvp.db"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Section 7: Core exceptions
print("=== SECTION 7: Core Exception Check ===")
failed = conn.execute(
    "SELECT ingestion_job_id, trigger_key, error, source FROM ingestion_jobs WHERE status='failed'"
).fetchall()
print(f"Total failed jobs: {len(failed)}")

schema_mismatch = 0
callback_auth = 0
db_locked = 0
no_connector = 0
wait_timeout = 0
datahub_bug = 0
dcp_remote = 0
unknown = 0
unknown_list = []

for j in failed:
    err = (j["error"] or "").lower()
    key = j["trigger_key"] or ""
    if "schema" in err and "mismatch" in err:
        schema_mismatch += 1
    elif "401" in err or "403" in err:
        if "0401" not in key and "0403" not in key:
            callback_auth += 1
        else:
            dcp_remote += 1
    elif "database is locked" in err:
        db_locked += 1
    elif "no connector" in err or "no_connector" in err:
        no_connector += 1
    elif "timeout" in err and ("wait" in err or "exceeded" in err):
        wait_timeout += 1
    elif "datahub" in err or "internal" in err:
        datahub_bug += 1
    elif any(kw in err for kw in ["dcp", "remote", "callback", "collect", "downloader", "planning", "failed"]):
        dcp_remote += 1
    else:
        unknown += 1
        unknown_list.append((j["ingestion_job_id"][:40], key, err[:80]))

print(f"  schema_mismatch: {schema_mismatch}")
print(f"  callback_401_403: {callback_auth}")
print(f"  database_locked: {db_locked}")
print(f"  no_connector: {no_connector}")
print(f"  wait_timeout: {wait_timeout}")
print(f"  datahub_bug: {datahub_bug}")
print(f"  dcp_remote_failure: {dcp_remote}")
print(f"  unknown_need_investigation: {unknown}")
for u in unknown_list[:10]:
    print(f"    UNKNOWN: {u}")

partial_count = conn.execute(
    "SELECT COUNT(*) as cnt FROM ingestion_jobs WHERE status='partial'"
).fetchone()[0]
print(f"  partial_jobs: {partial_count}")

# Row counts
print()
print("=== Row Counts ===")
tables = [
    "dcp_plan_year_project", "dcp_plan_year_single_project",
    "dcp_plan_project_progress", "dcp_plan_single_project_progress",
    "dcp_plan_bidsection_progress", "dcp_plan_dept_key_personnel",
    "dcp_project_tower", "dcp_project_substation",
    "dcp_project_line_branches", "dcp_project_line_sections",
    "dcp_safe_daily_meeting", "dcp_safe_daily_meeting_snapshot"
]
for t in tables:
    cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {cnt}")

# DDL check
print()
print("=== DDL Check ===")
ddl_content = open("src/datahub/storage/ddl.py").read()
alter_count = ddl_content.lower().count("alter table")
print(f"  ALTER TABLE count in ddl.py: {alter_count}")

conn.close()
