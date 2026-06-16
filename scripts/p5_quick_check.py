"""Quick check scheduler run progress."""
import sqlite3

conn = sqlite3.connect("data/datahub_mvp.db")
conn.row_factory = sqlite3.Row
steps = conn.execute(
    "SELECT step_order,command_name,status,started_at,finished_at FROM scheduled_run_steps WHERE run_id='run_dcp_daily_update_e082ac70949a' ORDER BY step_order"
).fetchall()
for s in steps:
    print(f"step {s[0]}: {s[1]} | {s[2]} | {s[3]}-{s[4]}")

# Also check next_run_at
plan = conn.execute("SELECT next_run_at FROM scheduled_plans WHERE plan_name='dcp_daily_update'").fetchone()
print(f"\ndcp_daily_update next_run_at: {plan[0]}")
conn.close()
