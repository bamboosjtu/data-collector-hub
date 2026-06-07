"""Check substations fan-out failure details."""
import sqlite3, os, json

DB = os.path.join(os.path.dirname(__file__), "..", "data", "datahub_mvp.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Check the failed substations parent
parent = "ing_refresh_substations_for_current_plan_projects_c5875b4ae727"
row = c.execute("SELECT status, error, result_json FROM ingestion_jobs WHERE ingestion_job_id = ?", (parent,)).fetchone()
print(f"Status: {row[0]}")
print(f"Error: {row[1]}")
print(f"Result: {row[2]}")

# Check WAL mode
print("\n=== Journal Mode ===")
mode = c.execute("PRAGMA journal_mode").fetchone()[0]
print(f"  journal_mode: {mode}")

# Check database integrity
print("\n=== Integrity Check ===")
result = c.execute("PRAGMA integrity_check").fetchone()[0]
print(f"  integrity: {result}")

conn.close()
