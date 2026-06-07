# DCP MVP Smoke Run

版本: mvp-dcp-plugin-ingestion-beta

## 前置条件

- Python 3.12+ / uv 已安装
- downloader-dcp 运行在 `http://localhost:8010`
- DCP 站点凭证已配置在 downloader-dcp 侧

## 1. 启动 Hub

```powershell
cd data-collector-hub
uv run python run.py
```

启动后确认:

```powershell
# 健康检查
curl http://localhost:8000/health
# 期望: {"status":"ok","schema_version":6}

# 元数据确认
curl http://localhost:8000/metadata
# 期望: 包含 plugins: [dcp], tables: [dcp_plan_projects, ...]
```

管理界面: `http://localhost:8501`

## 2. 运行核心 Command

### 2.1 年度计划（当前）

```powershell
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_annual_plans_current\"}"
```

记录返回的 `ingestion_job_id`。

### 2.2 项目进度

```powershell
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_plan_progress\"}"
```

### 2.3 关键人员

```powershell
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_dept_key_personnel\"}"
```

## 3. 验证 Row Count

```powershell
# 年度计划-项目级
curl "http://localhost:8000/api/v1/plan/projects?year=2025" ^
  -H "X-API-Key: dev-admin-key"

# 年度计划-单项级
curl "http://localhost:8000/api/v1/plan/single-projects?year=2025" ^
  -H "X-API-Key: dev-admin-key"

# 项目进度
curl "http://localhost:8000/api/v1/plan/project-progress" ^
  -H "X-API-Key: dev-admin-key"

# 关键人员
curl "http://localhost:8000/api/v1/plan/dept-key-personnel" ^
  -H "X-API-Key: dev-admin-key"
```

或通过运维面板查看:

```powershell
curl "http://localhost:8000/api/v1/ops/table-stats?table=dcp_plan_projects" ^
  -H "X-API-Key: dev-admin-key"
# 期望: {"table":"dcp_plan_projects","row_count":N,"last_updated":"..."}
```

确认各表 `row_count > 0`。

## 4. 验证 Parent/Child Jobs

Fan-out command 会创建 parent job 和多个 child jobs:

```powershell
# 触发 fan-out（以杆塔为例）
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_towers_for_current_plan_projects\"}"
```

记录 parent `ingestion_job_id`，然后:

```powershell
# 查看 parent job 状态
curl "http://localhost:8000/ingestion/v1/jobs/{parent_job_id}" ^
  -H "X-API-Key: dev-admin-key"
# 期望: status=running 或 completed

# 查看 child jobs
curl "http://localhost:8000/ingestion/v1/jobs/{parent_job_id}/children" ^
  -H "X-API-Key: dev-admin-key"
# 期望: 返回多个 child job，每个对应一个 projectCode
```

确认:
- parent job 存在且 status 为 completed
- children 数量与当前年度计划项目数一致
- 每个 child job 的 status 为 completed

## 5. 验证 Failed Jobs

```powershell
# 列出所有 jobs
curl "http://localhost:8000/ingestion/v1/jobs" ^
  -H "X-API-Key: dev-admin-key"
```

确认:
- 无 unexpected failed jobs
- 如果有 failed job，检查 `error_message` 字段
- 已知可能失败: DCP 站点返回空数据（空壳行会被 skipped，不计为失败）

## 6. 验证 Callback 200

downloader-dcp 回调 Hub 后，Hub 返回 202 Accepted:

```powershell
# 查看入库消息
curl "http://localhost:8000/ingestion/v1/messages" ^
  -H "X-API-Key: dev-admin-key"
```

确认:
- 每条 message 的 `status` 为 `accepted`
- `table_count` 和 `row_count` 符合预期
- `skipped_rows` 字段记录了被跳过的空壳行数量
- `skipped_details` 列出了跳过原因和涉及的表

也可直接查看 table_writes:

```powershell
curl "http://localhost:8000/ingestion/v1/table-writes" ^
  -H "X-API-Key: dev-admin-key"
```

确认每条 write 记录的 `row_count` > 0。

## 7. 验证 Daily Meeting 单日回补

```powershell
# 回补指定日期范围
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_daily_meetings_by_range\",\"params\":{\"startDate\":\"2025-06-01\",\"endDate\":\"2025-06-01\"}}"
```

确认:
- job 创建成功
- 回调完成后 `dcp_daily_meeting` 表有对应日期的数据

```powershell
curl "http://localhost:8000/api/v1/safety/daily-meetings?date=2025-06-01" ^
  -H "X-API-Key: dev-admin-key"
```

注意: daily_meeting 表当前标记为 DEFERRED，数据完整性取决于 DCP 站点返回。

## 8. 验证 Snapshot 业务时段测试

```powershell
# 触发今日站班会快照
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_daily_meeting_snapshot\"}"
```

确认:

```powershell
curl "http://localhost:8000/api/v1/safety/daily-meeting-snapshot" ^
  -H "X-API-Key: dev-admin-key"
# 期望: 返回今日站班会数据（如果 DCP 站点有数据）
```

注意: 此 command 为 downloader_sync 类型，直接调用 downloader-dcp，非 fan-out。

## 环境变量参考

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATAHUB_DB_PATH` | `data/datahub_mvp.db` | SQLite 数据库路径 |
| `DATAHUB_PLUGIN_DIR` | `plugins` | 插件目录 |
| `DATAHUB_CALLBACK_BASE_URL` | `http://localhost:8000` | 回调基础 URL |
| `DATAHUB_CALLBACK_API_KEY` | `dev-ingestion-key` | 回调 API Key |

## API Key 参考

| Key | Scope | 用途 |
|-----|-------|------|
| `dev-admin-key` | admin, ingestion, query | 管理操作、触发任务、查询数据 |
| `dev-ingestion-key` | ingestion | downloader-dcp 回调用 |
