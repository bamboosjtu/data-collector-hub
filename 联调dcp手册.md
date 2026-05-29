# DataCollectorHub 与 downloader-dcp 联调手册

本文用于真实联调 DataCollectorHub `trigger_runtime` 与 downloader-dcp `/sync`。当前自动化验证 `tests/phase5_api_runtime.py` 使用 `FakeExternalClient`，只能证明 DataHub 侧会构造正确的 sync 请求；本手册覆盖真实 downloader-dcp 服务、outbox callback、DataHub 入库和查询验收。

## 1. 联调目标

验证完整链路：

```text
DataHub POST /ingestion/v1/jobs
  -> DataHub core.trigger_runtime POST downloader-dcp /sync
  -> downloader-dcp 执行采集
  -> downloader-dcp outbox POST DataHub /ingestion/v1/table-batches
  -> DataHub 校验 TableBatch v1
  -> DataHub 幂等写 SQLite
  -> DataHub 查询 API 返回业务 DTO
```

DataHub 不参与 DCP 登录、加密、瑞数、分页、前置请求、参数派生或账号池调度。这些全部由 downloader-dcp 负责。

## 2. 默认端口和配置

DataCollectorHub 当前默认：

| 项 | 默认值 | 来源 |
|---|---|---|
| DataHub API | `http://localhost:8000` | `run.py` |
| DataHub callback base URL | `http://localhost:8000` | `DATAHUB_CALLBACK_BASE_URL` / `Settings.callback_base_url` |
| DataHub DB | `data/datahub_mvp.db` | `DATAHUB_DB_PATH` |
| Plugin 目录 | `plugins` | `DATAHUB_PLUGIN_DIR` |
| DCP downloader base URL | `http://localhost:8010` | `plugins/dcp/plugin.yaml` |
| 本地 admin key | `dev-admin-key` | DataHub 初始化写入 SQLite |

DCP 插件当前声明的 downloader connector：

```yaml
connector:
  type: downloader_sync
  base_url: http://localhost:8010
  timeout_seconds: 30
```

如果 downloader-dcp 不在本机 `8010`，先修改 `plugins/dcp/plugin.yaml` 的 `connector.base_url`，然后重启 DataHub。

如果 downloader-dcp 运行在容器里，`localhost` 的含义会变成容器自身。此时必须把 `DATAHUB_CALLBACK_BASE_URL` 设置为 downloader-dcp 容器能访问到的 DataHub 地址，例如 `http://host.docker.internal:8000` 或局域网 IP。

## 3. 联调前检查

### 3.1 检查 DataHub 代码基线

在 `D:\vibe-coding\DataCollectorHub`：

```powershell
uv run python tests\phase6_acceptance.py
uv run pytest tests -q
```

期望：

```text
phase0 ok
phase1 ok
phase2 ok
phase3 ok
phase4 ok
phase5 ok
phase6 ok
1 passed
```

### 3.2 检查 DCP 插件声明

```powershell
uv run python tests\phase2_dcp_plugin.py
```

期望：

```text
phase2 ok
```

这证明 DataHub 侧已注册 DCP commands、15 张业务表和 15 条 query routes。

### 3.3 确认 downloader-dcp 可用

在 downloader-dcp 项目内启动服务。具体命令以 downloader-dcp 仓库为准，联调要求是它必须暴露：

```text
POST http://localhost:8010/sync
GET  http://localhost:8010/sync/jobs/{downloader_job_id}
```

用 PowerShell 先探测服务端口：

```powershell
Invoke-WebRequest -Method GET http://localhost:8010/ -UseBasicParsing
```

如果根路径无 GET 接口但服务已启动，可直接用 `/sync` 做 dry request。缺少必填字段返回 4xx 也说明服务可达：

```powershell
Invoke-WebRequest `
  -Method POST `
  -Uri http://localhost:8010/sync `
  -ContentType "application/json" `
  -Body "{}" `
  -UseBasicParsing
```

服务不可达时，先不要触发 DataHub job；否则 DataHub job 会被标记为 `failed`，错误通常是连接被拒绝或超时。

## 4. 启动 DataHub

### 4.1 本机同端口联调

在 `D:\vibe-coding\DataCollectorHub`：

```powershell
$env:DATAHUB_CALLBACK_BASE_URL = "http://localhost:8000"
$env:DATAHUB_DB_PATH = "data\datahub_dcp_integration.db"
uv run python run.py --api-host 0.0.0.0 --api-port 8000 --dashboard-port 8501
```

启动后验证：

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/plugins
Invoke-RestMethod http://localhost:8000/schemas
```

期望 `/health`：

```json
{
  "status": "ok",
  "service": "datahub",
  "schema_version": 2
}
```

期望 `/plugins` 中包含：

```json
{
  "name": "dcp",
  "connector_type": "downloader_sync"
}
```

### 4.2 跨机器或容器联调

假设 downloader-dcp 所在环境能访问 DataHub 的地址是 `http://192.168.1.20:8000`：

```powershell
$env:DATAHUB_CALLBACK_BASE_URL = "http://192.168.1.20:8000"
$env:DATAHUB_DB_PATH = "data\datahub_dcp_integration.db"
uv run python run.py --api-host 0.0.0.0 --api-port 8000 --dashboard-port 8501
```

然后在 downloader-dcp 所在机器或容器中确认能访问：

```powershell
Invoke-RestMethod http://192.168.1.20:8000/health
```

如果 downloader-dcp 无法访问该地址，outbox 会一直重试，DataHub 不会收到 `/ingestion/v1/table-batches`。

## 5. 联调命令清单

DCP 插件当前支持以下 trigger job：

| job_type | required params | 推荐联调用途 |
|---|---|---|
| `plan_professional_all` | `planYear` | 年度计划 13 张表批量验证 |
| `year_progress_project_domain` | `year` | `replace_scope` 写入模式验证 |
| `safety_daily_meeting_range` | `startDate`, `endDate` | 安全站班会表验证 |
| `project_tech_full` | `projectCode` | 项目技术数据触发验证；是否有对应表取决于 downloader 输出与插件 schema |
| `daily_meeting_today_snapshot` | `date` | 单日快照触发验证 |
| `daily_meeting_yesterday_final` | `date` | 昨日终版触发验证 |

建议先用 `plan_professional_all` 或 `safety_daily_meeting_range`，因为当前 `plugins/dcp/tables.yaml` 已覆盖对应业务表。

## 6. 触发真实 `/sync`

### 6.1 触发年度计划采集

```powershell
$headers = @{ "X-API-Key" = "dev-admin-key" }
$body = @{
  job_type = "plan_professional_all"
  params = @{
    planYear = "2026"
  }
  debug = $false
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Method POST `
  -Uri http://localhost:8000/ingestion/v1/jobs `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

期望 DataHub 立即返回 `202`，body 形如：

```json
{
  "ingestion_job_id": "ing_plan_professional_all_xxx",
  "downloader_job_id": "job_plan_professional_all_2026_xxx",
  "status": "accepted"
}
```

记录返回的 `ingestion_job_id` 和 `downloader_job_id`，后续排查会用到。

### 6.2 触发年度进度领域表

```powershell
$headers = @{ "X-API-Key" = "dev-admin-key" }
$body = @{
  job_type = "year_progress_project_domain"
  params = @{
    year = "2026"
  }
  debug = $false
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Method POST `
  -Uri http://localhost:8000/ingestion/v1/jobs `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

该表使用 `replace_scope`，同一年再次成功回调会先删除 `year=2026` 旧数据再写入新数据。

### 6.3 触发安全站班会日期范围

```powershell
$headers = @{ "X-API-Key" = "dev-admin-key" }
$body = @{
  job_type = "safety_daily_meeting_range"
  params = @{
    startDate = "2026-06-01"
    endDate = "2026-06-04"
  }
  debug = $false
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Method POST `
  -Uri http://localhost:8000/ingestion/v1/jobs `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

查询时使用 downloader callback 中写入的 `dateRange`。如果约定为 `2026-06-01~2026-06-04`，查询命令见第 8 节。

## 7. 观察 downloader-dcp 状态

DataHub `/ingestion/v1/jobs` 的 `accepted` 只表示 downloader-dcp 接受了 `/sync`。真实采集和 outbox 投递状态要看 downloader-dcp。

用第 6 节返回的 `downloader_job_id`：

```powershell
$downloaderJobId = "job_plan_professional_all_2026_xxx"
Invoke-RestMethod "http://localhost:8010/sync/jobs/$downloaderJobId"
```

重点看：

- collect 是否成功。
- 是否生成 TableBatch。
- outbox 是否有 pending/delivering/delivered/failed。
- callback URL 是否为 DataHub `/ingestion/v1/table-batches`。

如果 downloader-dcp 支持结果接口，也可以查看：

```powershell
Invoke-RestMethod "http://localhost:8010/sync/jobs/$downloaderJobId/result"
```

如果状态显示 outbox `failed` 或持续 `pending`，优先检查第 10 节。

## 8. 验证 DataHub 已接收入库

### 8.1 查看 DataHub job

```powershell
$headers = @{ "X-API-Key" = "dev-admin-key" }
$ingestionJobId = "ing_plan_professional_all_xxx"

Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/ingestion/v1/jobs/$ingestionJobId" `
  -Headers $headers
```

关注字段：

- `status`: `/sync` 返回后通常是 `accepted`；收到 callback 后可能仍显示 `running`，这是当前 MVP 的聚合状态。
- `message_received`: 收到的 TableBatch message 数。
- `row_count`: 已写入行数。
- `producer_status_json`: downloader-dcp `/sync` 的返回。
- `error`: 触发阶段错误。

### 8.2 查看 callback messages

```powershell
Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/ingestion/v1/messages?limit=20" `
  -Headers $headers
```

期望看到：

```text
status = succeeded
dataset_key = plan_professional / year_progress_project_domain / safety_daily_meeting
payload_hash 非空
row_count >= 0
```

如果 status 是 `failed`，看 `error` 字段。常见值：

- `unknown_dataset`
- `unknown_table`
- `table_dataset_mismatch`
- `schema_mismatch`
- `missing_primary_key`
- `missing_scope_values`
- `idempotency_conflict`
- `payload_hash_conflict`

### 8.3 查看 table writes

```powershell
Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/ingestion/v1/table-writes?limit=50" `
  -Headers $headers
```

每个成功写入的 table 应有一条 `table_writes` 记录，关注：

- `table_name`
- `write_mode`
- `row_count`
- `inserted_count`
- `deleted_count`

`replace_scope` 表二次写入时，`deleted_count` 应能反映同 scope 旧数据删除数量。

## 9. 验证查询 API

### 9.1 年度计划进度管理

```powershell
Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/api/v1/plan/progress-management?planYear=2026&limit=5" `
  -Headers $headers
```

期望：

- 返回 `items` 数组。
- item 只包含 `plugins/dcp/tables.yaml` 声明的业务列。
- 不包含 `_ingest_message_id`、`_ingest_job_id` 等元数据列。
- 不包含 DCP 原始 envelope 或 raw record。

### 9.2 年度进度领域表

```powershell
Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/api/v1/year-progress/project-domain?year=2026&limit=5" `
  -Headers $headers
```

如果第一次查询有数据，再触发一次 `year_progress_project_domain`，期望同一年 scope 被替换，而不是重复追加。

### 9.3 安全站班会

```powershell
Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/api/v1/safety/daily-meetings?dateRange=2026-06-01~2026-06-04&limit=5" `
  -Headers $headers
```

如果返回为空，先到 `/ingestion/v1/messages` 查看实际 callback 的 `scope_key` 或业务行中的 `dateRange` 约定。查询参数必须与入库行字段值完全一致。

## 10. 常见问题排查

### 10.1 DataHub 触发 job 返回 502

现象：

```json
{
  "detail": {
    "error": "external_sync_failed"
  }
}
```

处理：

1. 确认 downloader-dcp 已启动。
2. 确认 `plugins/dcp/plugin.yaml` 中 `connector.base_url` 正确。
3. 在 DataHub 机器上执行：

```powershell
Invoke-WebRequest -Method POST -Uri http://localhost:8010/sync -ContentType "application/json" -Body "{}" -UseBasicParsing
```

能收到 downloader-dcp 的 4xx 业务错误，说明网络可达；连接拒绝或超时说明服务/端口不可达。

### 10.2 downloader-dcp accepted，但 DataHub 没有 message

处理顺序：

1. 查 downloader job 状态：

```powershell
Invoke-RestMethod "http://localhost:8010/sync/jobs/$downloaderJobId"
```

2. 确认 outbox 中 callback URL 是：

```text
http://localhost:8000/ingestion/v1/table-batches
```

或你设置的 `DATAHUB_CALLBACK_BASE_URL + /ingestion/v1/table-batches`。

3. 如果 downloader-dcp 在容器内，不能使用 `localhost:8000` 指向宿主 DataHub，改用宿主可达地址。
4. 确认 DataHub callback endpoint 需要 API key。当前 DataHub 的 `/ingestion/v1/table-batches` 强制 `X-API-Key` scope `ingestion`。真实 downloader-dcp 如果没有在 callback 中携带 `X-API-Key`，会收到 401。

重要：如果 downloader-dcp 当前 http_callback sink 不支持配置 header，需要在两边约定一种方案：

- 推荐方案：downloader-dcp sink 支持 `headers: {"X-API-Key": "..."}`，DataHub 继续强制 ingestion scope。
- 临时本地方案：新增仅限本机联调的 callback key 注入或测试配置，不建议关闭 DataHub 鉴权。

在 downloader-dcp 支持 headers 后，期望 `/sync` sink payload 类似：

```json
{
  "type": "http_callback",
  "url": "http://localhost:8000/ingestion/v1/table-batches",
  "headers": {
    "X-API-Key": "dev-admin-key"
  }
}
```

当前 DataHub `trigger_runtime` 只发送 `type` 和 `url`，未发送 sink headers。因此真实联调前必须确认 downloader-dcp 是否有默认 callback header 配置，或先实现 sink header 支持。

### 10.3 DataHub message failed: unknown_table

含义：downloader-dcp 回调了 DataHub 未注册的表。

处理：

1. 查看失败 message：

```powershell
Invoke-RestMethod "http://localhost:8000/ingestion/v1/messages?limit=20" -Headers $headers
```

2. 找到 error 中的 table name。
3. 确认该表是否应进入 MVP。
4. 如果应进入 MVP，在 `plugins/dcp/tables.yaml` 注册表 schema，并在需要时补充 query route。
5. 重启 DataHub，让 registry 重新加载插件。
6. downloader-dcp outbox 会重试同一 message；若已超过重试上限，需要在 downloader-dcp 侧重新投递或重新触发 sync。

### 10.4 DataHub message failed: schema_mismatch

含义：row 中有未知列、字段类型不匹配、非空字段为空或主键缺失。

处理：

1. 从 DataHub `ingestion_messages.received_payload_json` 查看原始 TableBatch。
2. 对比 `plugins/dcp/tables.yaml` 对应 table 的 `columns`。
3. 未注册但需要保留的溢出字段，应由 producer 放入已声明的 `extra` json 列；DataHub 不静默透传未知列。
4. 修复 schema 或 producer 输出后，等待 downloader-dcp outbox 重试。

### 10.5 DataHub message failed: table_dataset_mismatch

含义：TableBatch 顶层 `dataset_key` 与目标 table 在 `tables.yaml` 中声明的 `dataset_key` 不一致。

处理：

1. 确认 downloader-dcp 生成的 `dataset_key`。
2. 确认 `plugins/dcp/tables.yaml` 中该 table 的 `dataset_key`。
3. 两侧必须统一。DataHub 不允许一个 dataset 的 batch 写入另一个 dataset 的表。

### 10.6 重复投递与幂等

downloader-dcp outbox 是 at-least-once。重复 callback 是正常情况。

DataHub 期望行为：

- 同 `message_id` + 同 `payload_hash`：返回 2xx，body `duplicate_accepted`。
- 同 `message_id` + 不同 `payload_hash`：返回 409 `payload_hash_conflict`。
- 同 `idempotency_key` + 不同 `message_id`：返回 409 `idempotency_conflict`。

手动验证重复投递时，可以从 downloader-dcp outbox 重放同一 payload；不要手工改 `payload_hash`。

## 11. SQLite 直接排查

默认联调 DB：

```text
data/datahub_dcp_integration.db
```

如果本机安装了 sqlite3：

```powershell
sqlite3 data\datahub_dcp_integration.db ".tables"
sqlite3 data\datahub_dcp_integration.db "select message_id,status,dataset_key,row_count,error from ingestion_messages order by id desc limit 10;"
sqlite3 data\datahub_dcp_integration.db "select table_name,write_mode,row_count,inserted_count,deleted_count from table_writes order by id desc limit 20;"
```

查看业务表样例：

```powershell
sqlite3 data\datahub_dcp_integration.db "select planYear,id,prjCode,prjName from dcp_plan_progress_management where planYear='2026' limit 5;"
sqlite3 data\datahub_dcp_integration.db "select year,id,prjCode,prjName from dcp_year_progress_project_domain where year='2026' limit 5;"
```

不要直接修改业务表或元数据表。正式入库必须经过 `/ingestion/v1/table-batches`。

## 12. 最小验收清单

一次联调完成需满足：

1. DataHub `/health` 正常。
2. DataHub `/plugins` 显示 `dcp` plugin。
3. DataHub `POST /ingestion/v1/jobs` 返回 `202 accepted`。
4. downloader-dcp `/sync/jobs/{downloader_job_id}` 显示采集执行成功或进入投递流程。
5. DataHub `/ingestion/v1/messages` 至少出现一条 `succeeded` callback message。
6. DataHub `/ingestion/v1/table-writes` 出现对应业务表写入记录。
7. 对应 query route 能查到业务 DTO。
8. 查询响应不包含 `_ingest_*` 元数据列、不包含 raw DCP envelope。
9. 重复投递同一 message 时 DataHub 返回 2xx `duplicate_accepted`。
10. 若 schema mismatch，DataHub 返回非 2xx，downloader-dcp outbox 能保留并重试。

## 13. 当前已知联调缺口

当前 DataHub 代码已经实现真实 `/sync` 调用，但自动化测试仍只覆盖 FakeExternalClient。真实联调前重点确认：

1. downloader-dcp http_callback 是否能携带 `X-API-Key` header。
2. downloader-dcp 生成的 table names 是否全部在 `plugins/dcp/tables.yaml` 注册。
3. downloader-dcp 生成的 `dataset_key` 是否与 DataHub table schema 一致。
4. downloader-dcp 对 `dateRange`、`planYear`、`year` 等 scope 字段的值格式是否与 query route 预期一致。
5. 跨机器/容器时，`DATAHUB_CALLBACK_BASE_URL` 是否为 downloader-dcp 可访问地址。

若第 1 项不满足，真实 callback 会被 DataHub API key 鉴权拒绝，这是联调必须先解决的接口契约问题。
