# DCP Plugin MVP 验收记录

> 日期：2026-06-06
> plugin.yaml 版本：v9
> 对应架构文档：MVP_ARCHITECTURE.md 第 20 章

---

## 1. 结构验收结果

| 检查项 | 结果 |
|---|---|
| dcp_plan_sgcc_year 不作为业务表持久化 | PASS |
| dcp_plan_progress 不作为业务表持久化 | PASS |
| dcp_line_section 不作为业务表持久化（normalizer source） | PASS |
| 12 张业务表均无 raw 字段 | PASS |
| core 无 DCP 业务逻辑硬编码 | PASS |
| normalizer 消费 source table 后不持久化 source | PASS |
| extra 只保存未声明字段，不保存完整 raw | PASS |

## 2. 调度验收结果

| 检查项 | 结果 |
|---|---|
| 14 个 command 全部注册 | PASS |
| downloader_sync 触发链路 | PASS |
| fan_out 触发链路（project fan-out） | PASS |
| date_range_fan_out 触发链路（daily meeting 分片） | PASS |
| auto_params 解析（yesterday/today） | PASS |
| 父子任务关联（parent_job_id） | PASS |
| 子任务可独立重试 | PASS |

## 3. 真实数据入库验收

| 检查项 | 结果 | 说明 |
|---|---|---|
| dcp_plan_projects | PASS | 1704 行（plan_sgcc_year normalizer） |
| dcp_plan_single_projects | PASS | normalizer 展开 |
| dcp_plan_project_progress | PASS | 767 行（plan_progress normalizer type=1） |
| dcp_plan_single_project_progress | PASS | 2328 行（plan_progress normalizer type=2） |
| dcp_plan_bidding_section_progress | PASS | 2631 行（plan_progress normalizer type=3） |
| dcp_plan_dept_key_personnel | PASS | 1053 行，主键去重无冲突 |
| dcp_tower | PASS | 14 行，138 列字段化 |
| dcp_substation | PASS | 1 行，字段化 |
| dcp_line_branches | PASS | 3 行（line_section normalizer 外层） |
| dcp_line_sections | PASS | 8 行（line_section normalizer 内层 sectionDTOList） |
| dcp_daily_meeting | 待验证 | 需要 downloader 可达 |
| dcp_daily_meeting_snapshot | 待验证 | 需要 downloader 可达 |

### 真实验收计划（需要 downloader-dcp 运行）

1. 选择 dcp_plan_projects 中一个 prjCode
2. 调用 `refresh_towers_for_project` / `refresh_substations_for_project` / `refresh_line_sections_for_project`
3. 验证对应表有数据或明确返回无数据
4. 调用 `refresh_daily_meetings_by_range` 跑单日
5. 确认 dcp_daily_meeting 有数据或明确返回无数据
6. 调用 `backfill_daily_meetings_by_range` 跑 3 天范围
7. 确认生成 3 个 child jobs

## 4. Command 清单（14 个）

| # | Command | 类型 | trigger 类型 | required_params | 用途 |
|---|---|---|---|---|---|
| 1 | refresh_annual_plans_history | 全量 | downloader_sync | [] | 刷新历史年度计划 |
| 2 | refresh_annual_plans_current | 增量 | downloader_sync | [] | 刷新今年年度计划 |
| 3 | refresh_plan_progress | 全量 | downloader_sync | [] | 刷新项目进度 |
| 4 | refresh_dept_key_personnel | 全量 | downloader_sync | [] | 刷新关键人员 |
| 5 | refresh_towers_for_project | 单项目 | downloader_sync | [projectCode] | 刷新指定项目杆塔 |
| 6 | refresh_substations_for_project | 单项目 | downloader_sync | [projectCode] | 刷新指定项目变电站 |
| 7 | refresh_line_sections_for_project | 单项目 | downloader_sync | [projectCode] | 刷新指定项目架线区段 |
| 8 | refresh_towers_for_current_plan_projects | 批量 fan-out | fan_out | [] | 批量刷新今年项目杆塔 |
| 9 | refresh_substations_for_current_plan_projects | 批量 fan-out | fan_out | [] | 批量刷新今年项目变电站 |
| 10 | refresh_line_sections_for_current_plan_projects | 批量 fan-out | fan_out | [] | 批量刷新今年项目架线区段 |
| 11 | refresh_daily_meetings_by_range | 单日期范围 | downloader_sync | [startDate, endDate] | 刷新指定日期范围站班会 |
| 12 | backfill_daily_meetings_by_range | 日期分片 fan-out | date_range_fan_out | [startDate, endDate] | 批量回补站班会 |
| 13 | refresh_daily_meetings_yesterday | 昨日增量 | downloader_sync + auto_params | [] | 自动刷新昨日站班会 |
| 14 | refresh_daily_meeting_snapshot | 今日快照 | downloader_sync | [] | 刷新今日站班会快照 |

## 5. 业务表清单（12 张）

| 表名 | 主键 | 写入模式 | raw 字段 | 行数 |
|---|---|---|---|---|
| dcp_plan_projects | [prjCode] | replace_scope | 无 | 1704 |
| dcp_plan_single_projects | [singleProjectCode] | replace_scope | 无 | - |
| dcp_plan_project_progress | [prjCode] | replace_scope | 无 | 767 |
| dcp_plan_single_project_progress | [singleProjectCode] | replace_scope | 无 | 2328 |
| dcp_plan_bidding_section_progress | [biddingSectionCode] | replace_scope | 无 | 2631 |
| dcp_plan_dept_key_personnel | [originalIdCard, positionCode] | upsert | 无 | 1053 |
| dcp_tower | [singleProjectCode, id] | upsert | 无 | 14 |
| dcp_substation | [singleProjectCode, id] | upsert | 无 | 1 |
| dcp_line_branches | [biddingSectionCode, branchId] | upsert | 无 | 3 |
| dcp_line_sections | [biddingSectionCode, sectionId] | upsert | 无 | 8 |
| dcp_daily_meeting | [date, id] | upsert | 无 | 待验证 |
| dcp_daily_meeting_snapshot | [date] | upsert | 无 | 待验证 |

## 6. Normalizer 清单（4 个）

| source_table | targets | handler |
|---|---|---|
| dcp_plan_sgcc_year | dcp_plan_projects, dcp_plan_single_projects | normalize_plan_sgcc_year |
| dcp_plan_progress | dcp_plan_project_progress, dcp_plan_single_project_progress, dcp_plan_bidding_section_progress | normalize_plan_progress |
| dcp_plan_dept_key_personnel | dcp_plan_dept_key_personnel | normalize_plan_dept_key_personnel |
| dcp_line_section | dcp_line_branches, dcp_line_sections | normalize_line_section |

## 7. 暂缓项

| 项目 | 状态 | 说明 |
|---|---|---|
| dcp_daily_meeting 字段补全 | 暂缓 | 当前 11 列，待确认完整字段列表 |
| dcp_daily_meeting_snapshot 字段补全 | 暂缓 | 待确认完整字段列表 |
| fan-out 并发控制 | 暂缓 | 当前 max_concurrency=1，后续调优 |
| scheduler 定时触发 | 暂缓 | 当前手动触发，后续接入 APScheduler |
| fallback_chunk_days 自动降级 | 暂缓 | 7 天太大时降为 1 天，待实现 |
