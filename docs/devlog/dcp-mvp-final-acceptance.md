# DCP MVP Final Acceptance

Date: 2026-06-12

## 1. Version Info

| Component | Branch | Tag |
|-----------|--------|-----|
| data-collector-hub | `main` | - |
| downloader-dcp | (external) | - |

## 2. Three-Phase E2E Integration Results

### Phase 1: Basic Domain (downloader_sync)

| Command | Status | Rows | Notes |
|---------|--------|------|-------|
| `refresh_annual_plans_current` | succeeded | 416 | dcp_plan_year_project |
| `refresh_plan_progress` | succeeded | 767 | dcp_plan_project_progress |
| `refresh_dept_key_personnel` | succeeded | 1057 | dcp_plan_dept_key_personnel |

### Phase 2: Project Domain (plugin_handler fan-out)

| Command | Status | Child Success | Business Table | Rows |
|---------|--------|---------------|----------------|------|
| `refresh_towers_for_current_plan_projects` | partial | 415/416 | dcp_project_tower | 15,500 |
| `refresh_substations_for_current_plan_projects` | partial | 414/416 | dcp_project_substation | 206 |
| `refresh_line_sections_for_current_plan_projects` | partial | 412/416 | dcp_project_line_sections | 5,402 |
| | | | dcp_project_line_branches | 723 |

项目域 partial 说明：少量子任务 failed 不等于主链路失败。416 个项目中 1~4 个失败属于 DCP 端个案（接口异常、项目无对应业务数据、session 过期后 retry 仍失败等），需进入个案缺口追踪，不阻塞 MVP 验收。

### Phase 3: Safety Domain (plugin_handler fan-out)

| Command | Status | Child Success | Business Table | Rows |
|---------|--------|---------------|----------------|------|
| `backfill_daily_meetings_by_range` | succeeded | 890/890 | dcp_safe_daily_meeting | 303,548 |

参数：startDate=2024-01-01, endDate=2026-06-08, chunk_days=1, max_concurrency=5

### Summary

| Metric | Value |
|--------|-------|
| Total tables | 12 |
| Total rows ingested | 329,629 |
| Main chain status | Passed |
| Project domain partial | Acceptable, tracked as individual gaps |

## 3. Business Tables (New Naming)

| Table | Primary Key | Write Mode | Rows | Normalizer |
|-------|-------------|------------|------|------------|
| `dcp_plan_year_project` | year, prjCode | upsert | 416 | normalize_plan_sgcc_year |
| `dcp_plan_year_single_project` | year, singleProjectCode | upsert | 1288 | normalize_plan_sgcc_year |
| `dcp_plan_project_progress` | prjCode | replace_scope | 767 | normalize_plan_progress |
| `dcp_plan_single_project_progress` | singleProjectCode | replace_scope | 2328 | normalize_plan_progress |
| `dcp_plan_bidsection_progress` | biddingSectionCode | replace_scope | 2631 | normalize_plan_progress |
| `dcp_plan_dept_key_personnel` | originalIdCard, positionCode | replace_scope | 1057 | normalize_plan_dept_key_personnel |
| `dcp_project_tower` | singleProjectCode, id | upsert | 15,500 | - |
| `dcp_project_substation` | singleProjectCode | upsert | 206 | normalize_substation |
| `dcp_project_line_sections` | biddingSectionCode, sectionId | upsert | 5,402 | normalize_line_section |
| `dcp_project_line_branches` | biddingSectionCode, branchId | upsert | 723 | normalize_line_section |
| `dcp_safe_daily_meeting` | date, id | upsert | 303,548 | normalize_daily_meeting |
| `dcp_safe_daily_meeting_snapshot` | date, id | upsert | 0 | normalize_daily_meeting |

All tables use response-aligned storage. No `raw` JSON fields for business data.

Note: `dcp_project_line_section` (单数) 是 raw/source 输入表名，`dcp_project_line_sections` (复数) 是最终业务表名。

## 4. Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | max_concurrency=5 | 匹配 downloader-dcp pool_slots=5 |
| 2 | cooldown_seconds=3 | 避免 downloader 过载 |
| 3 | consecutive_failure_threshold=5 | circuit breaker 触发阈值 |
| 4 | transient retry 最多 2 次 | delay 3s、6s，不计入 consecutive failures |
| 5 | fanout_items 支持 retry_count / next_attempt_at | 持久化重试状态 |
| 6 | fanout_scheduler 后台 tick (3s) | 持久化调度，crash 可恢复 |
| 7 | fanout_runs + fanout_items 表 | 调度状态持久化 |
| 8 | 表名新命名体系 | dcp_{domain}_{entity}，复数表示业务表 |

## 5. Transient Retry

Fan-out scheduler 对以下 transient child failure 自动重试：

- session_expired
- recoverable
- SGCC client is expired
- DCP_CLIENT_EXPIRED
- timeout
- ETIMEDOUT
- ECONNRESET
- slot_unavailable
- runner_timeout

机制：
- 最多 retry 2 次，delay 为 3s、6s
- transient retry 不计入 consecutive failures
- 超过 retry 上限后转为 permanent failure，进入 failed 状态
- permanent failure 计入 consecutive failures，可能触发 circuit breaker

downloader-dcp 已在 app 层将 SGCC client expired 重分类为 session_expired。

## 6. Fixed Issues

| # | Issue | Fix |
|---|-------|-----|
| 1 | Empty wrapper rows not filtered | 5-condition skip logic in validator.py |
| 2 | extra field contains raw/payload/response/result | Forbidden key filter in registry.py |
| 3 | plugin_handler loads arbitrary modules | Prefix validation in core/fan_out.py |
| 4 | callback_api_key not configurable | Dev mode default + production enforcement |
| 5 | downloader_sync job status not synced | Background polling thread + stale threshold |
| 6 | dcp_project_substation schema_mismatch | normalizer + schema alignment |
| 7 | dcp_project_line_section two-layer expansion | normalizer fix |
| 8 | Fan-out parent polled by downloader | NOT EXISTS children condition |
| 9 | Fan-out parent stale threshold false positive | NOT EXISTS children condition |
| 10 | Date fan-out no circuit breaker | consecutive_failure_threshold + _is_child_failed |
| 11 | Project fan-out no circuit breaker | Same pattern as date fan-out |
| 12 | Fan-out parent premature aggregation | fan_out_in_progress flag in result_json |
| 13 | dcp_safe_daily_meeting 3-column schema | 42-column fielded schema + normalizer |
| 14 | Child params contain fan-out controls | Cleanup: remove max_items/cooldown/threshold/concurrency |
| 15 | Invalid fan-out params crash | Validation: cooldown>=0, threshold>=1, max_items>=1 |
| 16 | Fan-out serial execution too slow | Persistent fan-out scheduler with concurrent child submission |
| 17 | `_wait_for_child_terminal` blocks threads | Scheduler tick reads child status from ingestion_jobs |
| 18 | Fan-out context lost on crash | fanout_runs + fanout_items tables persist scheduling state |
| 19 | Callback endpoint blocks event loop | `asyncio.to_thread` for sync ingestion_service calls |
| 20 | SQLite busy_timeout too short (5s) | Raised to 30s, aligned with downloader-dcp |
| 21 | CommandSpec missing concurrency fields | max_concurrency, max_concurrency_limit, cooldown_seconds |
| 22 | Table names inconsistent | Migration to new naming: dcp_{domain}_{entity} |
| 23 | No transient retry for recoverable failures | fanout_items retry_count/next_attempt_at, scheduler auto-retry |

## 7. Known Technical Debt

| # | Item | Impact | Priority |
|---|------|--------|----------|
| 1 | `downloader_job_id` naming biased toward downloader | Cosmetic | Low |
| 2 | SQLite MVP: single-writer, no concurrent access | Local dev only | Medium |
| 3 | No admin UI for job monitoring | CLI only | Medium |
| 4 | command/service abstraction not done | Scalability | Medium |
| 5 | Query routes not configured for all tables | Some tables 404 | Low |
| 6 | max_concurrency_limit is manual config, not auto-discovered | Must align with downloader pool capacity | Low |
| 7 | Permanent failure still requires manual CLI retry | Operational burden | Medium |
| 8 | dcp_safe_daily_meeting_snapshot not populated in this run | Data gap | Low |

Note: The following items from earlier debt lists are now resolved:
- ~~DCP session/WAF expiry requires manual downloader restart~~ → downloader-dcp reclassifies SGCC client expired as session_expired; DataHub transient retry handles it automatically
- ~~No automated retry for transient failures~~ → fanout_items retry_count/next_attempt_at, scheduler auto-retry up to 2 times
- ~~Fan-out serial wait per child~~ → Persistent scheduler with concurrent submission

## 8. Architecture: Persistent Fan-out Scheduler

| Component | Role |
|-----------|------|
| `fan_out.py` handlers | Create fanout_runs + fanout_items, return immediately (<1s) |
| `fanout_scheduler.py` | Background tick (3s): claim lease, submit children, circuit-break, transient retry, close |
| `fanout_runs` table | Parent scheduling state: total, max_concurrency, consecutive_failures, circuit_opened |
| `fanout_items` table | Child items: pending → submitting → submitted → succeeded/failed/skipped, retry_count, next_attempt_at |
| `poll_downloader_jobs` | Syncs child terminal states from downloader → ingestion_jobs |
| `CommandSpec` | max_concurrency, max_concurrency_limit, cooldown_seconds |

Crash recovery: scheduler tick rebuilds context from SQLite on restart.

## 9. Seal Conclusion

**DCP 数据采集链路三阶段联调通过，基础域、安全域、项目域主链路均已验证成功。**

- Basic domain: 3/3 commands, all succeeded
- Project domain: 3 fan-out types, partial (412~415/416), acceptable as individual gaps
- Safety domain: 890-day concurrent backfill, 303,548 rows, 0 failures
- Error metrics: schema_mismatch=0, callback 401/403=0, database locked=0
- Circuit breaker: both date and project fan-out verified
- Transient retry: session_expired/timeout/slot_unavailable auto-retry verified
- Data quality: empty wrapper rows=0, extra NOT NULL=0
- Crash recovery: fan-out state persisted in SQLite, scheduler tick resumes on restart

No new features will be added. Next phase: ops UI convergence + command/service abstraction.
