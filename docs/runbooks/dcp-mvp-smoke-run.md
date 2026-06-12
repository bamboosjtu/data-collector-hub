# DCP MVP Smoke Run

> **WARNING: 本文档仅限开发/联调环境使用，不得用于生产部署。**
> 生产环境必须显式配置 `DATAHUB_CALLBACK_API_KEY` 和 `DATAHUB_DEV_MODE=0`。

版本: mvp-dcp-final

## 前置条件

- Python 3.12+ / uv 已安装
- downloader-dcp 运行在 `http://localhost:8010`
- DCP 站点凭证已配置在 downloader-dcp 侧
- 环境变量 `DATAHUB_DEV_MODE=1`（默认开启，dev 模式自动创建引导 API Key）

## 1. 启动 Hub

```powershell
cd data-collector-hub
uv run python run.py
```

启动后确认:

```powershell
# 健康检查
Invoke-RestMethod -Uri http://localhost:8000/health -Method Get
# 期望: status=ok, schema_version=N

# 元数据确认
Invoke-RestMethod -Uri http://localhost:8000/metadata -Method Get
# 期望: 包含 plugins: [dcp], tables: [dcp_plan_year_project, ...]
```

运维面板: `http://localhost:8000/ops`（长期运维方向，当前功能有限，首次访问需输入 API Key）

## 2. 启动 downloader-dcp

```powershell
cd downloader-dcp
uv run python -m downloader_dcp
# 默认运行在 http://localhost:8010
```

DCP 站点凭证需在 downloader-dcp 侧配置。

确认:

```powershell
Invoke-RestMethod -Uri http://localhost:8010/health -Method Get
# 期望: status=ok, pool_slots=5
```

## 3. 三阶段执行顺序

按以下顺序依次触发，每步等待完成后再执行下一步：

### 阶段 1：基础数据

```powershell
# 1. 年度计划
uv run python -m src.datahub.cli trigger refresh_annual_plans_current

# 2. 项目进度
uv run python -m src.datahub.cli trigger refresh_plan_progress

# 3. 关键人员
uv run python -m src.datahub.cli trigger refresh_dept_key_personnel
```

### 阶段 2：项目域

```powershell
# 4. 杆塔（fan-out，416 个子任务）
uv run python -m src.datahub.cli trigger refresh_towers_for_current_plan_projects

# 5. 变电站（fan-out）
uv run python -m src.datahub.cli trigger refresh_substations_for_current_plan_projects

# 6. 架线区段（fan-out）
uv run python -m src.datahub.cli trigger refresh_line_sections_for_current_plan_projects
```

### 阶段 3：安全域

```powershell
# 7. 站班会回补（fan-out，890 个子任务）
uv run python -m src.datahub.cli trigger backfill_daily_meetings_by_range --params startDate=2024-01-01 endDate=2026-06-08 chunk_days=1 max_concurrency=5
```

### API 方式触发

```powershell
$API_KEY = "dev-admin-key"

# 基础域
Invoke-RestMethod -Uri http://localhost:8000/ingestion/v1/jobs -Method Post -Headers @{"X-API-Key"=$API_KEY; "Content-Type"="application/json"} -Body '{"command":"refresh_annual_plans_current"}'

# 项目域 fan-out
Invoke-RestMethod -Uri http://localhost:8000/ingestion/v1/jobs -Method Post -Headers @{"X-API-Key"=$API_KEY; "Content-Type"="application/json"} -Body '{"command":"refresh_towers_for_current_plan_projects"}'

# 安全域回补
Invoke-RestMethod -Uri http://localhost:8000/ingestion/v1/jobs -Method Post -Headers @{"X-API-Key"=$API_KEY; "Content-Type"="application/json"} -Body '{"command":"backfill_daily_meetings_by_range","params":{"startDate":"2024-01-01","endDate":"2026-06-08","chunk_days":1,"max_concurrency":5}}'
```

## 4. 查看 Job 状态

```powershell
# 列出所有 jobs
uv run python -m src.datahub.cli jobs

# 查看单个 job
uv run python -m src.datahub.cli job <job_id>

# 查看 fan-out 子任务
uv run python -m src.datahub.cli children <parent_job_id>

# 查看表行数
uv run python -m src.datahub.cli tables
```

## 5. 验收 SQL

以下 SQL 直接在 SQLite 上执行：

```powershell
uv run python -c "
import sqlite3
conn = sqlite3.connect('data/datahub_mvp.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('YOUR_SQL_HERE')
for row in cur.fetchall():
    print(dict(row))
conn.close()
"
```

或使用 sqlite3 CLI：

```powershell
sqlite3 data/datahub_mvp.db "YOUR_SQL_HERE"
```

### 5.1 Job 状态分布

```sql
SELECT status, COUNT(*) FROM ingestion_jobs GROUP BY status;
```

### 5.2 按 trigger_key 分组的状态分布

```sql
SELECT
  trigger_key,
  status,
  COUNT(*)
FROM ingestion_jobs
GROUP BY trigger_key, status
ORDER BY trigger_key, status;
```

### 5.3 失败 Job 按 trigger_key 分组

```sql
SELECT
  trigger_key,
  COUNT(*) AS failed_count
FROM ingestion_jobs
WHERE status = 'failed'
GROUP BY trigger_key
ORDER BY failed_count DESC;
```

### 5.4 各业务表行数

```sql
SELECT 'dcp_plan_year_project' AS tbl, COUNT(*) FROM dcp_plan_year_project
UNION ALL SELECT 'dcp_plan_year_single_project', COUNT(*) FROM dcp_plan_year_single_project
UNION ALL SELECT 'dcp_plan_project_progress', COUNT(*) FROM dcp_plan_project_progress
UNION ALL SELECT 'dcp_plan_single_project_progress', COUNT(*) FROM dcp_plan_single_project_progress
UNION ALL SELECT 'dcp_plan_bidsection_progress', COUNT(*) FROM dcp_plan_bidsection_progress
UNION ALL SELECT 'dcp_plan_dept_key_personnel', COUNT(*) FROM dcp_plan_dept_key_personnel
UNION ALL SELECT 'dcp_project_tower', COUNT(*) FROM dcp_project_tower
UNION ALL SELECT 'dcp_project_substation', COUNT(*) FROM dcp_project_substation
UNION ALL SELECT 'dcp_project_line_sections', COUNT(*) FROM dcp_project_line_sections
UNION ALL SELECT 'dcp_project_line_branches', COUNT(*) FROM dcp_project_line_branches
UNION ALL SELECT 'dcp_safe_daily_meeting', COUNT(*) FROM dcp_safe_daily_meeting
UNION ALL SELECT 'dcp_safe_daily_meeting_snapshot', COUNT(*) FROM dcp_safe_daily_meeting_snapshot;
```

### 5.5 Daily Meeting 日期覆盖范围

```sql
SELECT
  MIN(date) AS min_date,
  MAX(date) AS max_date,
  COUNT(DISTINCT date) AS day_count,
  COUNT(*) AS row_count
FROM dcp_safe_daily_meeting;
```

### 5.6 项目域 scope 覆盖

```sql
-- 杆塔覆盖的 distinct project
SELECT COUNT(DISTINCT singleProjectCode) FROM dcp_project_tower;

-- 变电站覆盖的 distinct project
SELECT COUNT(DISTINCT singleProjectCode) FROM dcp_project_substation;

-- 架线区段覆盖的 distinct bidding section
SELECT COUNT(DISTINCT biddingSectionCode) FROM dcp_project_line_sections;
```

### 5.7 Fan-out 汇总

```sql
SELECT
  parent_job_id,
  trigger_key,
  COUNT(*) AS total_children,
  SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) AS succeeded,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
  SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) AS skipped
FROM ingestion_jobs
WHERE parent_job_id IS NOT NULL
GROUP BY parent_job_id, trigger_key
ORDER BY parent_job_id;
```

## 6. Partial / Failed 判断

| 父 Job 状态 | 含义 | 处理 |
|-------------|------|------|
| `succeeded` | 全部子任务成功 | 无需处理 |
| `partial` | 有成功子任务，也有少量 failed/skipped | 检查失败子任务，进入个案追踪 |
| `failed` | 无成功结果或全部失败 | 需排查根因 |

**项目域 partial 不等于主链路失败。** 416 个项目中 1~4 个失败属于 DCP 端个案，不阻塞 MVP 验收。

**安全域 `backfill_daily_meetings_by_range` 应要求 890/890 succeeded。** 如果不是 890/890，需排查是否有 DCP session 过期或网络问题。

**区分 succeeded row_count=0 和 failed：**
- `succeeded` + `row_count=0`：DCP 端该日期/项目无数据，正常
- `failed`：采集过程出错，需要追踪

## 7. 失败子任务查询

### 7.1 查询所有 failed child jobs

```sql
SELECT
  ingestion_job_id,
  parent_job_id,
  trigger_key,
  params_json,
  status,
  current_message,
  error,
  created_at,
  updated_at
FROM ingestion_jobs
WHERE status = 'failed'
ORDER BY created_at;
```

### 7.2 按 trigger_key 分组统计失败数

```sql
SELECT
  trigger_key,
  COUNT(*) AS failed_count
FROM ingestion_jobs
WHERE status = 'failed'
GROUP BY trigger_key
ORDER BY failed_count DESC;
```

### 7.3 提取失败子任务的 projectCode

```sql
SELECT
  ingestion_job_id,
  trigger_key,
  json_extract(params_json, '$.projectCode') AS projectCode,
  error,
  current_message
FROM ingestion_jobs
WHERE status = 'failed'
  AND trigger_key LIKE 'refresh_%_for_project'
ORDER BY trigger_key, projectCode;
```

### 7.4 导出失败 projectCode 清单

```sql
SELECT DISTINCT
  json_extract(params_json, '$.projectCode') AS projectCode,
  trigger_key
FROM ingestion_jobs
WHERE status = 'failed'
  AND json_extract(params_json, '$.projectCode') IS NOT NULL
ORDER BY projectCode;
```

### 7.5 Fanout items 重试状态

```sql
SELECT
  fi.item_id,
  fi.status,
  fi.retry_count,
  fi.next_attempt_at,
  fi.error_message,
  fr.trigger_key
FROM fanout_items fi
JOIN fanout_runs fr ON fi.run_id = fr.run_id
WHERE fi.retry_count > 0
ORDER BY fi.retry_count DESC;
```

## 8. Replay 指引

### 8.1 Replay 单个失败项目

```powershell
# 查看失败 job 详情
uv run python -m src.datahub.cli job <failed_job_id>

# 重试单个失败 job
uv run python -m src.datahub.cli retry <failed_job_id>
```

或按 projectCode 手动触发：

```powershell
# 杆塔
uv run python -m src.datahub.cli trigger refresh_towers_for_project --params projectCode=XXXX

# 变电站
uv run python -m src.datahub.cli trigger refresh_substations_for_project --params projectCode=XXXX

# 架线区段
uv run python -m src.datahub.cli trigger refresh_line_sections_for_project --params projectCode=XXXX
```

### 8.2 何时需要重新跑 parent fan-out

- **不需要**：仅 1~4 个子任务失败，属于个案缺口，replay 单个即可
- **需要**：大面积失败（如 circuit breaker 打开导致大量 skipped），需排查根因后重新跑 parent fan-out

### 8.3 幂等保障

重复跑不会导致数据重复：
- `upsert` 模式：按主键更新
- `replace_scope` 模式：按 scope 替换
- `message_id` + `idempotency_key` + `payload_hash` 重复抑制

## 9. Transient Retry 与 Circuit Breaker

### 9.1 Transient Retry

Fan-out scheduler 对以下 transient child failure 自动重试：

- `session_expired`
- `recoverable`
- `SGCC client is expired`
- `DCP_CLIENT_EXPIRED`
- `timeout`
- `ETIMEDOUT`
- `ECONNRESET`
- `slot_unavailable`
- `runner_timeout`

机制：
- 最多 retry 2 次，delay 为 3s、6s
- transient retry 不计入 consecutive failures
- 超过 retry 上限后转为 permanent failure，进入 `failed` 状态
- permanent failure 计入 consecutive failures

### 9.2 判断 transient retry 是否生效

```sql
-- 查看有重试记录的 fanout items
SELECT item_id, status, retry_count, next_attempt_at, error_message
FROM fanout_items
WHERE retry_count > 0
ORDER BY retry_count DESC;
```

如果 `retry_count > 0` 且 `status = 'succeeded'`，说明 transient retry 生效。

### 9.3 Circuit Breaker

当 consecutive failures 达到阈值（默认 5）时，circuit breaker 打开，剩余 pending 子任务被标记为 `skipped`。

```sql
-- 检查 circuit breaker 是否打开
SELECT run_id, trigger_key, consecutive_failures, circuit_opened
FROM fanout_runs
WHERE circuit_opened = 1;
```

### 9.4 哪些失败可接受为 MVP 个案缺口

- DCP 端项目接口异常（个别 projectCode）
- 项目无对应业务数据（row_count=0 的 succeeded）
- session_expired 经过 retry 后仍失败（个别）
- upstream timeout（个别）

### 9.5 哪些失败必须阻塞发布

- `unknown_table`：schema 注册有问题
- 大面积 422：校验逻辑有误
- `message_failed` 持续增长：入库链路有问题
- circuit breaker 大量 skipped：DCP 源端大面积故障
- daily meeting 不是 890/890：安全域回补不完整

## 10. 查询 API 验证

```powershell
$API_KEY = "dev-admin-key"

# 年度计划
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/plan/projects?year=2025" -Method Get -Headers @{"X-API-Key"=$API_KEY}

# 项目进度
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/plan/project-progress" -Method Get -Headers @{"X-API-Key"=$API_KEY}

# 关键人员
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/plan/dept-key-personnel" -Method Get -Headers @{"X-API-Key"=$API_KEY}

# 杆塔
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/project/towers?singleProjectCode=XXXX" -Method Get -Headers @{"X-API-Key"=$API_KEY}

# 站班会
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/safety/daily-meetings?date=2025-06-01" -Method Get -Headers @{"X-API-Key"=$API_KEY}

# 单表统计
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ops/table-stats?table=dcp_project_tower" -Method Get -Headers @{"X-API-Key"=$API_KEY}
```

## 环境变量参考

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATAHUB_DB_PATH` | `data/datahub_mvp.db` | SQLite 数据库路径 |
| `DATAHUB_PLUGIN_DIR` | `plugins` | 插件目录 |
| `DATAHUB_CALLBACK_BASE_URL` | `http://localhost:8000` | 回调基础 URL |
| `DATAHUB_CALLBACK_API_KEY` | dev 模式自动填充 | 回调 API Key，**生产环境必须显式配置** |
| `DATAHUB_DEV_MODE` | `1` | dev 模式开关，`0` 为生产模式 |

## Job 状态名参考

| 状态 | 含义 |
|------|------|
| `triggering` | 正在触发 downloader |
| `running` | 正在执行 |
| `succeeded` | 成功完成 |
| `failed` | 执行失败 |
| `accepted` | 入库消息已接受 |
| `partial` | 部分成功（fan-out 有成功也有失败子任务） |
| `conflict` | 幂等冲突 |
| `skipped` | 被 circuit breaker 跳过 |

## CLI 速查

```powershell
uv run python -m src.datahub.cli commands                    # 列出可用命令
uv run python -m src.datahub.cli trigger <command>           # 触发命令
uv run python -m src.datahub.cli trigger <cmd> --params k=v  # 带参数触发
uv run python -m src.datahub.cli jobs                        # 列出 jobs
uv run python -m src.datahub.cli job <id>                    # 查看 job 详情
uv run python -m src.datahub.cli children <id>               # 查看子 jobs
uv run python -m src.datahub.cli retry <id>                  # 重试失败 job
uv run python -m src.datahub.cli tables                      # 表行数 + 最后写入
```
