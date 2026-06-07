# DCP MVP Real Run Log

Template version: 1
Tag: mvp-dcp-plugin-ingestion-beta

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

### Run #1 — _fill_date_

- command:
- params:
- trigger_type:
- parent_job_id:
- child_jobs:
    - total:
    - success_count:
    - failed_count:
    - failed_details:
- table_counts:
- skipped_rows:
- skipped_details:
- callback_status:
- notes:
- operator:

### Run #2 — _fill_date_

- command:
- params:
- trigger_type:
- parent_job_id:
- child_jobs:
    - total:
    - success_count:
    - failed_count:
    - failed_details:
- table_counts:
- skipped_rows:
- skipped_details:
- callback_status:
- notes:
- operator:

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
