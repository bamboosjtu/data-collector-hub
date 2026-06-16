"""Update plan configs in DB with P5.1 timeout settings."""
import sqlite3, json, sys
sys.path.insert(0, ".")
from src.datahub.core.services.collection_plan_service import DCP_INITIAL_FULL_LOAD_CONFIG, DCP_DAILY_UPDATE_CONFIG

conn = sqlite3.connect("data/datahub_mvp.db")
conn.execute("UPDATE scheduled_plans SET config_json = ? WHERE plan_name = ?",
             (json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False), "dcp_initial_full_load"))
conn.execute("UPDATE scheduled_plans SET config_json = ? WHERE plan_name = ?",
             (json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False), "dcp_daily_update"))
conn.commit()
print("Updated plan configs")

for name in ["dcp_initial_full_load", "dcp_daily_update"]:
    row = conn.execute("SELECT config_json FROM scheduled_plans WHERE plan_name = ?", (name,)).fetchone()
    if row:
        config = json.loads(row[0])
        wt = config.get("wait_timeout_seconds")
        pi = config.get("poll_interval_seconds")
        print(f"  {name}: wait_timeout_seconds={wt}, poll_interval_seconds={pi}")
    else:
        print(f"  {name}: NOT FOUND")
conn.close()
