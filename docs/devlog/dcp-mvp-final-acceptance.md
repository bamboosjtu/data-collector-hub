# DCP MVP Final Acceptance

Date: 2026-06-10

## 1. Version Info

| Component | Commit | Tag |
|-----------|--------|-----|
| data-collector-hub | `c55f93f` | `mvp-dcp-concurrent-fanout` |
| downloader-dcp | (external) | `v1.0.1` |

## 2. Verified Commands

### Basic Domain (downloader_sync)

| Command | Description | Verified |
|---------|-------------|----------|
| `refresh_annual_plans_current` | Current year plan projects | OK, 1704 rows |
| `refresh_plan_progress` | Plan progress overview | OK, 5726 rows |
| `refresh_dept_key_personnel` | Department key personnel | OK, 1055 rows |

### Project Domain (downloader_sync + plugin_handler fan-out)

| Command | Description | Verified |
|---------|-------------|----------|
| `refresh_towers_for_project` | Single project towers | OK |
| `refresh_substations_for_project` | Single project substations | OK, row_count=0 allowed |
| `refresh_line_sections_for_project` | Single project line sections | OK |
| `refresh_towers_for_current_plan_projects` | Fan-out: all projects towers | OK, 414/416 succeeded |
| `refresh_substations_for_current_plan_projects` | Fan-out: all projects substations | OK, circuit breaker verified |
| `refresh_line_sections_for_current_plan_projects` | Fan-out: all projects line sections | OK |

### Safety Domain (downloader_sync + plugin_handler fan-out)

| Command | Description | Verified |
|---------|-------------|----------|
| `refresh_daily_meetings_by_range` | Daily meetings by date range | OK, 158 rows (1 day) |
| `backfill_daily_meetings_by_range` | Date-range fan-out with circuit breaker | OK, 890-day concurrent verified |
| `refresh_daily_meetings_yesterday` | Yesterday incremental | OK |
| `refresh_daily_meeting_snapshot` | Meeting snapshot | OK, 219 rows |

## 3. Business Tables

| Table | Schema | Rows (approx) | Normalizer |
|-------|--------|---------------|------------|
| `dcp_plan_projects` | 87 columns | 1704 | normalize_plan_sgcc_year |
| `dcp_plan_single_projects` | 74 columns | - | normalize_plan_sgcc_year |
| `dcp_plan_project_progress` | 32 columns | - | normalize_plan_progress |
| `dcp_plan_single_project_progress` | 35 columns | - | normalize_plan_progress |
| `dcp_plan_bidding_section_progress` | 37 columns | 5726 | normalize_plan_progress |
| `dcp_plan_dept_key_personnel` | 7 columns | 1055 | normalize_plan_dept_key_personnel |
| `dcp_tower` | 131 columns | ~12000 | - |
| `dcp_substation` | 8 columns | 59 | normalize_substation |
| `dcp_line_branches` | 5 columns | - | normalize_line_section |
| `dcp_line_sections` | 18 columns | ~8000 | normalize_line_section |
| `dcp_daily_meeting` | 43 columns | 303548 | normalize_daily_meeting |
| `dcp_daily_meeting_snapshot` | 43 columns | ~127000 | normalize_daily_meeting |

All tables use response-aligned storage. No `raw` JSON fields for business data.

## 4. Real Run Results

### Basic Domain

| Command | Rows | Status |
|---------|------|--------|
| refresh_annual_plans_current | 1704 | succeeded |
| refresh_plan_progress | 5726 | succeeded |
| refresh_dept_key_personnel | 1055 | succeeded |

### Project Domain

| Fan-out | Total Projects | Succeeded | Failed | Notes |
|---------|---------------|-----------|--------|-------|
| towers | 416 | 414 | 2 | 2 request_failed, retry succeeded |
| substations | 20 (sample) | 20 | 0 | Circuit breaker verified, no false triggers |
| line_sections | 416 | verified | - | Two-layer expansion fixed |

### Safety Domain 890-Day Concurrent Backfill

| Metric | Value |
|--------|-------|
| Date range | 2024-01-01 ~ 2026-06-08 |
| Total chunks | 890 |
| Succeeded | 890 |
| Failed | 0 |
| Total rows | 303,548 |
| Dates with data | 843 / 890 |
| extra NOT NULL | 0 |
| schema_mismatch | 0 |
| max_concurrency | 5 |
| Duration | 115 min |
| Throughput | 7.4 writes/min, 2650 rows/min |

### Speed Comparison: Serial vs Concurrent

| Metric | Serial (max_concurrency=1) | Concurrent (max_concurrency=5) | Speedup |
|--------|---------------------------|-------------------------------|---------|
| Writes/min | 2.0 | 7.4 | **3.70x** |
| Rows/min | 745 | 2,650 | **3.56x** |
| Failed | 1 | 0 | - |

## 5. Fixed Issues

| # | Issue | Fix |
|---|-------|-----|
| 1 | Empty wrapper rows not filtered | 5-condition skip logic in validator.py |
| 2 | extra field contains raw/payload/response/result | Forbidden key filter in registry.py |
| 3 | plugin_handler loads arbitrary modules | Prefix validation in core/fan_out.py |
| 4 | callback_api_key not configurable | Dev mode default + production enforcement |
| 5 | downloader_sync job status not synced | Background polling thread + stale threshold |
| 6 | dcp_substation schema_mismatch | normalizer + schema alignment |
| 7 | dcp_line_section two-layer expansion | normalizer fix |
| 8 | Fan-out parent polled by downloader | NOT EXISTS children condition |
| 9 | Fan-out parent stale threshold false positive | NOT EXISTS children condition |
| 10 | Date fan-out no circuit breaker | consecutive_failure_threshold + _is_child_failed |
| 11 | Project fan-out no circuit breaker | Same pattern as date fan-out |
| 12 | Fan-out parent premature aggregation | fan_out_in_progress flag in result_json |
| 13 | dcp_daily_meeting 3-column schema | 42-column fielded schema + normalizer |
| 14 | Child params contain fan-out controls | Cleanup: remove max_items/cooldown/threshold/concurrency |
| 15 | Invalid fan-out params crash | Validation: cooldown>=0, threshold>=1, max_items>=1 |
| 16 | Fan-out serial execution too slow | Persistent fan-out scheduler with concurrent child submission |
| 17 | `_wait_for_child_terminal` blocks threads | Scheduler tick reads child status from ingestion_jobs (poller syncs) |
| 18 | Fan-out context lost on crash | fanout_runs + fanout_items tables persist scheduling state |
| 19 | Callback endpoint blocks event loop | `asyncio.to_thread` for sync ingestion_service calls |
| 20 | SQLite busy_timeout too short (5s) | Raised to 30s, aligned with downloader-dcp |
| 21 | CommandSpec missing concurrency fields | max_concurrency, max_concurrency_limit, cooldown_seconds |

## 6. Known Technical Debt

| # | Item | Impact | Priority |
|---|------|--------|----------|
| 1 | `downloader_job_id` naming biased toward downloader | Cosmetic | Low |
| 2 | ~~Fan-out serial wait per child~~ | ~~416 projects ~30min~~ | ~~Medium~~ **RESOLVED: persistent scheduler** |
| 3 | SQLite MVP: single-writer, no concurrent access | Local dev only | Medium |
| 4 | DCP session/WAF expiry requires manual downloader restart | Operational burden | High |
| 5 | No admin UI for job monitoring | CLI only | Medium |
| 6 | command/service abstraction not done | Scalability | Medium |
| 7 | Query routes not configured for all tables | Some tables 404 | Low |
| 8 | No automated retry for transient failures | Manual retry via CLI | Medium |
| 9 | max_concurrency_limit is manual config, not auto-discovered | Must align with downloader pool capacity | Low |

## 7. Architecture: Persistent Fan-out Scheduler

Fan-out execution changed from serial handler to persistent scheduler model:

| Component | Role |
|-----------|------|
| `fan_out.py` handlers | Create fanout_runs + fanout_items, return immediately (<1s) |
| `fanout_scheduler.py` | Background tick (3s): claim lease, submit children, circuit-break, close |
| `fanout_runs` table | Parent scheduling state: total, max_concurrency, consecutive_failures, circuit_opened |
| `fanout_items` table | Child items: pending → submitting → submitted → succeeded/failed/skipped |
| `poll_downloader_jobs` | Syncs child terminal states from downloader → ingestion_jobs |
| `CommandSpec` | max_concurrency, max_concurrency_limit, cooldown_seconds |

Crash recovery: scheduler tick rebuilds context from SQLite on restart.

## 8. Seal Conclusion

**DCP MVP ingestion chain accepted for local MVP validation.**

All critical paths verified:
- Basic domain: 3/3 commands, all succeeded
- Project domain: 3 fan-out types, circuit breaker verified
- Safety domain: 890-day concurrent backfill, 303,548 rows, 0 failures, 3.7x speedup
- Error metrics: schema_mismatch=0, callback 401/403=0, database locked=0, disk I/O=0
- Circuit breaker: both date and project fan-out verified
- Data quality: empty wrapper rows=0, extra NOT NULL=0
- Crash recovery: fan-out state persisted in SQLite, scheduler tick resumes on restart

No new features will be added. Next phase: ops UI convergence + command/service abstraction.
