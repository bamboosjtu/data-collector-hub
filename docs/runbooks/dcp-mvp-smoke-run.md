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
curl http://localhost:8000/health
# 期望: {"status":"ok","schema_version":N}

# 元数据确认
curl http://localhost:8000/metadata
# 期望: 包含 plugins: [dcp], tables: [dcp_plan_projects, ...]
```

管理界面: `http://localhost:8501`（debug/legacy 候选，不建议作为生产入口）
运维面板: `http://localhost:8000/ops`（长期运维方向，当前功能有限，首次访问需输入 API Key）

## 2. 运行核心 Command

以下示例使用 `$API_KEY` 代替实际 key。dev 模式下可使用自动创建的引导 key，或通过 `POST /admin/api-keys` 创建新 key。

```powershell
# 设置 API Key 变量（dev 模式引导 key，仅限本地开发）
$API_KEY = "dev-admin-key"
```

### 2.1 年度计划（当前）

```powershell
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: $API_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_annual_plans_current\"}"
```

记录返回的 `ingestion_job_id`。

### 2.2 项目进度

```powershell
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: $API_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_plan_progress\"}"
```

### 2.3 关键人员

```powershell
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: $API_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_dept_key_personnel\"}"
```

## 3. 验证 Row Count

```powershell
# 年度计划-项目级
curl "http://localhost:8000/api/v1/plan/projects?year=2025" ^
  -H "X-API-Key: $API_KEY"

# 年度计划-单项级
curl "http://localhost:8000/api/v1/plan/single-projects?year=2025" ^
  -H "X-API-Key: $API_KEY"

# 项目进度
curl "http://localhost:8000/api/v1/plan/project-progress" ^
  -H "X-API-Key: $API_KEY"

# 关键人员
curl "http://localhost:8000/api/v1/plan/dept-key-personnel" ^
  -H "X-API-Key: $API_KEY"
```

或通过运维面板 / CLI 查看:

```powershell
# 单表统计
curl "http://localhost:8000/api/v1/ops/table-stats?table=dcp_plan_projects" ^
  -H "X-API-Key: $API_KEY"
# 期望: {"table":"dcp_plan_projects","row_count":N,"last_updated":"..."}

# CLI 方式
uv run python -m src.datahub.cli tables
```

确认各表 `row_count > 0`。

## 4. 验证 Parent/Child Jobs

Fan-out command 会创建 parent job 和多个 child jobs:

```powershell
# 触发 fan-out（以杆塔为例）
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: $API_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_towers_for_current_plan_projects\"}"
```

记录 parent `ingestion_job_id`，然后:

```powershell
# 查看 parent job 状态
curl "http://localhost:8000/ingestion/v1/jobs/{parent_job_id}" ^
  -H "X-API-Key: $API_KEY"
# 期望: status=succeeded 或 running

# 查看 child jobs
curl "http://localhost:8000/ingestion/v1/jobs/{parent_job_id}/children" ^
  -H "X-API-Key: $API_KEY"
# 期望: 返回多个 child job，每个对应一个 projectCode

# CLI 方式
uv run python -m src.datahub.cli children {parent_job_id}
```

确认:
- parent job 存在且 status 为 `succeeded`
- children 数量与当前年度计划项目数一致
- 每个 child job 的 status 为 `succeeded`

## 5. 验证 Failed Jobs

```powershell
# 列出所有 jobs
curl "http://localhost:8000/ingestion/v1/jobs" ^
  -H "X-API-Key: $API_KEY"

# CLI 方式
uv run python -m src.datahub.cli jobs
```

确认:
- 无 unexpected `failed` jobs
- 如果有 failed job，检查 `error` 字段
- 已知可能失败: DCP 站点返回空数据（空壳行会被 skipped，不计为失败）

### 重试 Failed Job

```powershell
# API 方式
curl -X POST "http://localhost:8000/ingestion/v1/jobs/{failed_job_id}/retry" ^
  -H "X-API-Key: $API_KEY"

# CLI 方式
uv run python -m src.datahub.cli retry {failed_job_id}
```

## 6. 验证 Callback

downloader-dcp 回调 Hub 后，Hub 返回 **202 Accepted**:

```powershell
# 查看入库消息
curl "http://localhost:8000/ingestion/v1/messages" ^
  -H "X-API-Key: $API_KEY"
```

确认:
- 每条 message 的 `status` 为 `accepted`
- `table_count` 和 `row_count` 符合预期
- `skipped_rows` 字段记录了被跳过的空壳行数量
- `skipped_details` 列出了跳过原因和涉及的表

也可直接查看 table_writes:

```powershell
curl "http://localhost:8000/ingestion/v1/table-writes" ^
  -H "X-API-Key: $API_KEY"
```

确认每条 write 记录的 `row_count` > 0。

## 7. 验证 Daily Meeting 单日回补

```powershell
# 回补指定日期范围
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: $API_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_daily_meetings_by_range\",\"params\":{\"startDate\":\"2025-06-01\",\"endDate\":\"2025-06-01\"}}"
```

确认:
- job 创建成功
- 回调完成后 `dcp_daily_meeting` 表有对应日期的数据

```powershell
curl "http://localhost:8000/api/v1/safety/daily-meetings?date=2025-06-01" ^
  -H "X-API-Key: $API_KEY"
```

注意: daily_meeting 已字段化为 42 列，关键业务字段（singleProjectCode、biddingSectionCode、leaderName 等）可直接 SQL 查询。

## 8. 验证 Snapshot 业务时段测试

```powershell
# 触发今日站班会快照
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: $API_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_daily_meeting_snapshot\"}"
```

确认:

```powershell
curl "http://localhost:8000/api/v1/safety/daily-meeting-snapshot" ^
  -H "X-API-Key: $API_KEY"
# 期望: 返回今日站班会数据（如果 DCP 站点有数据）
```

注意: 此 command 为 downloader_sync 类型，直接调用 downloader-dcp，非 fan-out。

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
| `partial` | 部分成功 |
| `conflict` | 幂等冲突 |

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
