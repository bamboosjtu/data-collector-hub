# DCP MVP Real Run Log

Template version: 1
Tag: mvp-dcp-plugin-ingestion-beta2

## Run Record Template

Each run records one command execution and its outcomes.

```
### Run #N — YYYY-MM-DD HH:MM

- command: <command name>
- params: <JSON or "none">
- trigger_type: downloader_sync | plugin_handler
- parent_job_id: <id or "n/a">
- child_jobs:
    - total: N
    - success_count: N
    - failed_count: N
    - failed_details:
        - job_id: <id>, error: <message>
        - ...
- table_counts:
    - <table_name>: before=N → after=N (delta=+N)
    - ...
- skipped_rows: N
- skipped_details: <summary or "none">
- callback_status: 200 | failed
- notes: <free text or "none">
- operator: <name>
```

---

## Runs

### Run #1 — 2026-06-07 03:43

- command: refresh_annual_plans_current
- params: none
- trigger_type: downloader_sync
- parent_job_id: n/a
- job_id: ing_refresh_annual_plans_current_3e5aa10ad50c
- child_jobs:
    - total: 0
    - success_count: 0
    - failed_count: 0
    - failed_details: none
- table_counts:
    - dcp_plan_projects: before=0 → after=416 (delta=+416)
    - dcp_plan_single_projects: before=0 → after=1288 (delta=+1288)
- skipped_rows: 0
- skipped_details: none
- callback_status: 202 (after auth fix)
- notes: First callback attempt returned 401 (downloader-dcp OutboxDispatcher ignores per-job sink.headers). Fixed by deferring auth in Hub. Second attempt succeeded.
- operator: auto

### Run #2 — 2026-06-07 03:44

- command: refresh_plan_progress
- params: none
- trigger_type: downloader_sync
- parent_job_id: n/a
- job_id: ing_refresh_plan_progress_7d325ece4795
- child_jobs:
    - total: 0
    - success_count: 0
    - failed_count: 0
    - failed_details: none
- table_counts:
    - dcp_plan_project_progress: before=0 → after=0 (delta=0)
- skipped_rows: 0
- skipped_details: none
- callback_status: no callback received
- notes: downloader-dcp reported "stalled: no collect task completed within 180s". Hub job still shows "accepted" — status not updated because downloader_sync has no status polling. NEEDS FIX: Hub should poll downloader-dcp job status or accept status callback.
- operator: auto

### Run #3 — 2026-06-07 03:44

- command: refresh_dept_key_personnel
- params: none
- trigger_type: downloader_sync
- parent_job_id: n/a
- job_id: ing_refresh_dept_key_personnel_b4d186b1629b
- child_jobs:
    - total: 0
    - success_count: 0
    - failed_count: 0
    - failed_details: none
- table_counts:
    - dcp_plan_dept_key_personnel: before=0 → after=1054 (delta=+1054)
- skipped_rows: 0
- skipped_details: none
- callback_status: 202
- notes: Success.
- operator: auto

### Run #4 — 2026-06-07 03:50

- command: refresh_towers_for_project
- params: {projectCode: "1316A0240004"}
- trigger_type: downloader_sync
- parent_job_id: n/a
- job_id: ing_refresh_towers_for_project_1a1e377877fd
- child_jobs:
    - total: 0
    - success_count: 0
    - failed_count: 0
    - failed_details: none
- table_counts:
    - dcp_tower: before=0 → after=0 (delta=0)
- skipped_rows: 0
- skipped_details: none
- callback_status: no callback (no data)
- notes: downloader-dcp reported "all tasks already completed" with row_count=0. This project (娄底民丰500千伏变电站改扩建工程) has no tower data — it's a substation project.
- operator: auto

### Run #5 — 2026-06-07 03:50

- command: refresh_substations_for_project
- params: {projectCode: "1316A0240004"}
- trigger_type: downloader_sync
- parent_job_id: n/a
- job_id: ing_refresh_substations_for_project_3304fadfd837
- child_jobs:
    - total: 0
    - success_count: 0
    - failed_count: 0
    - failed_details: none
- table_counts:
    - dcp_substation: before=0 → after=0 (delta=0)
- skipped_rows: 0
- skipped_details: none
- callback_status: 422 (schema_mismatch)
- notes: **STOP CONDITION HIT: schema_mismatch: dcp_substation.id is required**. downloader-dcp sent substation data with id=None. The DCP API response field for substation ID may not map to "id" column. Needs investigation of DCP raw field names vs Hub schema column names.
- operator: auto

### Run #6 — 2026-06-07 03:50

- command: refresh_line_sections_for_project
- params: {projectCode: "1316A0240004"}
- trigger_type: downloader_sync
- parent_job_id: n/a
- job_id: ing_refresh_line_sections_for_project_57f0758d7993
- child_jobs:
    - total: 0
    - success_count: 0
    - failed_count: 0
    - failed_details: none
- table_counts:
    - dcp_line_sections: before=0 → after=0 (delta=0)
- skipped_rows: 0
- skipped_details: none
- callback_status: no callback (no data)
- notes: Same as towers — this project has no line section data.
- operator: auto

---

## Issues Found

### Issue 1: Auth 401 on callback (FIXED)
- downloader-dcp OutboxDispatcher uses global headers, ignores per-job sink.headers
- Fixed by deferring auth enforcement in Hub (auth.py)
- TODO: Re-enable strict auth when downloader-dcp supports per-job callback headers

### Issue 2: Job status not synced (OPEN)
- downloader_sync jobs stay "accepted" in Hub even when downloader-dcp reports "failed"
- Hub has no mechanism to poll downloader-dcp job status
- NEEDS: status callback endpoint or polling mechanism

### Issue 3: dcp_substation.id schema_mismatch (BLOCKING)
- downloader-dcp sends substation data with id=None
- Hub schema requires id (nullable=false, primary key)
- Root cause: DCP API response field name for substation ID may not be "id"
- NEEDS: Check DCP raw field names and align with Hub schema

### Issue 4: plan_progress stalled (OPEN)
- downloader-dcp reports "stalled: no collect task completed within 180s"
- May be WAF/rate limiting on DCP site
- NEEDS: Retry with longer timeout or investigate DCP site response

## Quick Reference: Available Commands

| Command | Params | Type |
|---------|--------|------|
| refresh_annual_plans_history | none | downloader_sync |
| refresh_annual_plans_current | none | downloader_sync |
| refresh_plan_progress | none | downloader_sync |
| refresh_dept_key_personnel | none | downloader_sync |
| refresh_towers_for_project | projectCode | downloader_sync |
| refresh_substations_for_project | projectCode | downloader_sync |
| refresh_line_sections_for_project | projectCode | downloader_sync |
| refresh_towers_for_current_plan_projects | none | plugin_handler (fan-out) |
| refresh_substations_for_current_plan_projects | none | plugin_handler (fan-out) |
| refresh_line_sections_for_current_plan_projects | none | plugin_handler (fan-out) |
| refresh_daily_meetings_by_range | startDate, endDate | downloader_sync |
| backfill_daily_meetings_by_range | startDate, endDate | plugin_handler (fan-out) |
| refresh_daily_meetings_yesterday | none | plugin_handler (fan-out) |
| refresh_daily_meeting_snapshot | none | downloader_sync |

## Quick Reference: Table Row Count Queries

```sql
SELECT 'dcp_plan_projects' AS tbl, COUNT(*) FROM dcp_plan_projects
UNION ALL SELECT 'dcp_plan_single_projects', COUNT(*) FROM dcp_plan_single_projects
UNION ALL SELECT 'dcp_plan_project_progress', COUNT(*) FROM dcp_plan_project_progress
UNION ALL SELECT 'dcp_plan_single_project_progress', COUNT(*) FROM dcp_plan_single_project_progress
UNION ALL SELECT 'dcp_plan_bidding_section_progress', COUNT(*) FROM dcp_plan_bidding_section_progress
UNION ALL SELECT 'dcp_plan_dept_key_personnel', COUNT(*) FROM dcp_plan_dept_key_personnel
UNION ALL SELECT 'dcp_tower', COUNT(*) FROM dcp_tower
UNION ALL SELECT 'dcp_substation', COUNT(*) FROM dcp_substation
UNION ALL SELECT 'dcp_line_branches', COUNT(*) FROM dcp_line_branches
UNION ALL SELECT 'dcp_line_sections', COUNT(*) FROM dcp_line_sections
UNION ALL SELECT 'dcp_daily_meeting', COUNT(*) FROM dcp_daily_meeting
UNION ALL SELECT 'dcp_daily_meeting_snapshot', COUNT(*) FROM dcp_daily_meeting_snapshot;
```

Or via API:

```powershell
curl -s http://localhost:8000/api/v1/ops/table-stats?table=dcp_tower -H "X-API-Key: dev-admin-key"
```
