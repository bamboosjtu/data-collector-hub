# DCP MVP Real Run Log（压缩版）

本文档是 DCP MVP 实际运行日志的压缩版本，仅保留关键里程碑、重大事件和最终验收数据。完整日志见 git 历史。

---

## Key Milestones

| Batch | Date | Scope | Key Result |
|-------|------|-------|------------|
| 1 | 2026-06-07 | Basic domain first attempt | 1/3 succeeded (plan_progress stalled, auth 401 fixed) |
| 2 | 2026-06-07 | Status polling verification | 2/3 succeeded (plan_progress still stalled) |
| 3 | 2026-06-07 | Full basic data success | 3/3 succeeded after downloader-dcp fix |
| 4 | 2026-06-07 | Re-run verification | 3/3 succeeded, upsert/replace_scope idempotent |
| 5 | 2026-06-07 | Single project verification | 4 projects x 3 commands = 12 jobs, all succeeded |
| 6 | 2026-06-07 | Fan-out verification (max_items=5) | CLI --params bug + poller fix, unintended full fan-out |
| 7 | 2026-06-07 | Clean fan-out retest (max_items=5) | 15/15 children succeeded, parent aggregation fixed |
| 8 | 2026-06-07 | Fan-out max_items=10 | 1 SQLite "database is locked" (retried OK) |
| 9 | 2026-06-07 | Fan-out max_items=20 | WAL + busy_timeout fix, disk I/O error from concurrent PRAGMA |
| 10 | 2026-06-07 | Fan-out max_items=50 | 148/150 succeeded, zero SQLite errors with WAL |
| 11 | 2026-06-07 | Post-normalizer full re-verification | 153/153 jobs succeeded, substation empty_shells=0 |
| 12 | 2026-06-07 | Fan-out max_items=100 | 300/300 succeeded, fan-out parent stale fix |
| 13 | 2026-06-07 | Full 416 fan-out | 1237/1248 (99.1%), all failures downloader-dcp side |
| 14 | 2026-06-08 | Retry failed children | 11/11 retry succeeded after downloader-dcp SQLite fix |
| 15 | 2026-06-08 | Safety domain daily meeting | 42-column fieldized schema, 14-day backfill 5294 rows |
| 15b | 2026-06-08 | Post-normalizer re-verification | extra NOT NULL=0, all fields independent columns |
| 16 | 2026-06-08 | 30-day backfill | 11015 rows, 30 dates, 0 failures |
| 17 | 2026-06-08 | 90-day backfill | 30628 rows, 90 dates, 0 failures |
| 18 | 2026-06-08 | 180-day backfill (first attempt) | FAILED: DCP safe.dailyMeeting request_failed all dates |
| 19 | 2026-06-08 | 180-day backfill (with circuit breaker) | 53320 rows, 182 dates, 0 failures |
| 20 | 2026-06-08 | 365-day backfill | 127092 rows, 362/365 succeeded, 1 transient retry |

---

## Critical Incidents

### 1. safe.dailyMeeting request_failed（Run #70）

**现象：** 180 天回补中，DCP `safe.dailyMeeting` API 对所有日期返回 `request_failed`，包括之前 90 天回补中成功的日期。

```
{'api': 'safe.dailyMeeting', 'stage': 'time_slice_collection',
 'message': '1 slice(s) failed for safe.dailyMeeting',
 'error_type': 'request_failed', 'retry_count': 0}
```

**根因：** DCP 会话/WAF 过期。downloader-dcp 的 DCP session 失效，导致所有后续请求被拒绝。

**修复：**
1. 重启 downloader-dcp 恢复 DCP session
2. 实现了 circuit breaker（连续失败阈值=5），防止在 DCP 源端故障时继续创建子任务
3. 新增 `_is_child_failed()` 和 `_wait_for_child_terminal()` 函数
4. 23 个测试覆盖 circuit breaker 逻辑

**影响：** 90 天数据（30628 行）完好无损，180 天回补未写入任何数据。修复后 180 天和 365 天回补均成功。

### 2. 项目 Fan-out 网络中断（Batch 13）

**现象：** 全量 416 项目 fan-out 中，9 个子任务失败（1237/1248 成功）。

**失败分类：**

| 错误类型 | 数量 | 来源 |
|----------|------|------|
| DCP API planning error | 4 | downloader-dcp |
| sink error: database is locked | 3 | downloader-dcp |
| sink error: no more rows available | 1 | downloader-dcp |
| sink error: transaction within transaction | 1 | downloader-dcp |

**修复：** downloader-dcp 实现 connection-per-operation 模式。Batch 14 重试全部 11 个失败子任务，11/11 成功。

### 3. SQLite 并发写入修复

**现象：** Fan-out 期间出现 "database is locked" 错误，以及并发 PRAGMA journal_mode=WAL 导致的 disk I/O error。

**修复：**
- **DataHub 侧：** WAL 模式 + busy_timeout=5000，PRAGMA journal_mode=WAL 仅在 `init_schema()` 中执行一次（不在每次连接时执行）
- **downloader-dcp 侧：** connection-per-operation 模式（每次操作使用独立连接，操作完成后立即关闭）

**验证：** max_items=50 及以上批次零 SQLite 错误。365 天回补（365 个子任务）零 database locked、零 disk I/O error。

---

## Final Acceptance Data

### 表行数

| Table | Final Rows |
|-------|-----------|
| dcp_plan_projects | 1704 |
| dcp_plan_single_projects | 1288 |
| dcp_plan_project_progress | 767 |
| dcp_plan_single_project_progress | 2328 |
| dcp_plan_bidding_section_progress | 2631 |
| dcp_plan_dept_key_personnel | 1055 |
| dcp_tower | 15520 |
| dcp_substation | 59 |
| dcp_line_sections | 5421 |
| dcp_line_branches | 720 |
| dcp_daily_meeting | 127092 |
| dcp_daily_meeting_snapshot | ~127000 |

### 365 天回补关键指标

| Metric | Value |
|--------|-------|
| Total rows | 127,092 |
| Dates with data | 351 / 365 |
| schema_mismatch | 0 |
| extra NOT NULL | 0 |
| callback 401/403 | 0 |
| database locked | 0 |
| Circuit breaker triggered | No |

---

## Issues Found and Fixed

| # | Issue | Fix |
|---|-------|-----|
| 1 | Auth 401 on callback | Deferred auth in Hub（downloader-dcp 忽略 per-job sink.headers） |
| 2 | Job status not synced | Background status poller（5s interval, 30min stale threshold） |
| 3 | dcp_substation.id schema_mismatch | normalizer + nullable id，primary_key 改为 [singleProjectCode] |
| 4 | plan_progress stalled | downloader-dcp 侧修复 |
| 5 | dcp_substation empty shell rows | normalize_substation normalizer（仅输出含业务字段的行） |
| 6 | Fan-out parent stale threshold | NOT EXISTS children 条件排除 fan-out parent |
| 7 | Fan-out parent polled as downloader job | NOT EXISTS children 条件排除 fan-out parent |
| 8 | Date fan-out no circuit breaker | consecutive_failure_threshold + _is_child_failed |

---

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
