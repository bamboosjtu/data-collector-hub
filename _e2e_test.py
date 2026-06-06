"""End-to-end test: send sample batch data to Hub and verify normalizer expansion."""
import json, httpx, os

HUB = "http://localhost:8000"
API_KEY = "dev-admin-key"
BATCHES = r"c:\Users\theTruth\Documents\projects\vibe-demo\downloader-dcp\tests\outputs"

def send_batch(filepath):
    with open(filepath, encoding="utf-8") as f:
        payload = json.load(f)
    # Override message_id and idempotency_key to avoid conflicts
    payload["message_id"] = f"msg_test_{os.path.basename(filepath)}"
    payload["idempotency_key"] = f"ik_test_{os.path.basename(filepath)}"
    r = httpx.post(f"{HUB}/ingestion/v1/table-batches", json=payload, headers={"X-API-Key": API_KEY}, timeout=30)
    return r

# Test 1: plan_sgcc_year normalizer
print("=== Test 1: plan_sgcc_year normalizer ===")
r = send_batch(os.path.join(BATCHES, "job_real_sgcc_year_current_41d69538", "batches", "001_plan_sgcc_year.json"))
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Test 2: plan_progress normalizer (three-level expansion)
print("\n=== Test 2: plan_progress normalizer ===")
r = send_batch(os.path.join(BATCHES, "job_real_progress_43ceede9", "batches", "001_plan_progress.json"))
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Test 3: plan_dept_key_personnel normalizer
print("\n=== Test 3: plan_dept_key_personnel normalizer ===")
r = send_batch(os.path.join(BATCHES, "job_real_dept_key_personnel_d586d692", "batches", "001_plan_dept_key_personnel.json"))
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Test 4: tower
print("\n=== Test 4: tower ===")
r = send_batch(os.path.join(BATCHES, "job_real_towers_fae16492", "batches", "001_tower.json"))
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Test 5: substation
print("\n=== Test 5: substation ===")
r = send_batch(os.path.join(BATCHES, "job_real_substations_055783fc", "batches", "001_substation.json"))
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Test 6: line_section
print("\n=== Test 6: line_section ===")
r = send_batch(os.path.join(BATCHES, "job_real_lines_e2f46404", "batches", "001_line_section.json"))
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
