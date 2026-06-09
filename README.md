# DataCollectorHub

DataCollectorHub 是独立 DataHub 服务。通过插件声明 schema、trigger 和 query routes，接收标准 TableBatch v1，负责 schema 校验、幂等写入、SQLite 存储、API key 授权和下游查询 API。

`downloader-dcp` 是外部 producer。DataCollectorHub 不实现 DCP 登录、页面抓取、瑞数、加密、分页、Cookie、业务参数派生或 DCP 协议细节。

## MVP Status

DCP MVP 已封板 (2026-06-09)。当前能力：

- 基础域：年度计划、项目进度、关键人员 — 全量通过
- 项目域：杆塔、变电站、架线区段 fan-out — 全量通过
- 安全域：站班会 365 天回补 — 127,092 行，0 数据质量问题
- Fan-out 熔断器：date 和 project fan-out 均已验证
- SQLite 稳定性：WAL + busy_timeout，connection-per-operation

详见 [docs/devlog/dcp-mvp-final-acceptance.md](docs/devlog/dcp-mvp-final-acceptance.md)。

## Quick Start

### 1. 启动 DataHub

```powershell
cd data-collector-hub
uv run python run.py
```

启动后确认：

```powershell
curl http://localhost:8000/health
# {"status":"ok","schema_version":N}
```

### 2. 启动 downloader-dcp

```powershell
cd downloader-dcp
uv run python -m downloader_dcp
# 默认运行在 http://localhost:8010
```

DCP 站点凭证需在 downloader-dcp 侧配置。

### 3. 跑 Smoke 测试

```powershell
# 单元测试（无外部依赖）
uv run pytest tests/unit/ -v

# 集成测试（需要 SQLite，不需要外部服务）
uv run pytest tests/integration/ -v

# 全量本地测试
uv run pytest tests/unit/ tests/integration/ -v

# E2E 测试（需要 DataHub + downloader-dcp 运行）
uv run pytest tests/e2e/ -v
```

或使用 smoke 脚本（需要 DataHub + downloader-dcp 运行）：

```powershell
uv run python scripts/smoke/verify_run.py
```

### 4. 触发采集

```powershell
# CLI 方式
uv run python -m src.datahub.cli commands                    # 列出可用命令
uv run python -m src.datahub.cli trigger refresh_annual_plans_current
uv run python -m src.datahub.cli jobs                        # 查看 jobs
uv run python -m src.datahub.cli retry <job_id>              # 重试失败 job

# API 方式
curl -X POST http://localhost:8000/ingestion/v1/jobs ^
  -H "X-API-Key: dev-admin-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"command\":\"refresh_annual_plans_current\"}"
```

完整 smoke 流程见 [docs/runbooks/dcp-mvp-smoke-run.md](docs/runbooks/dcp-mvp-smoke-run.md)。

## Architecture

```
src/datahub/
  app.py                  # FastAPI app factory
  settings.py             # environment-backed settings
  core/                   # plugin loading, registry, trigger runtime, time_utils
  ingestion/              # TableBatch v1 models, validation, idempotency, service
  storage/                # SQLite DDL, metadata tables, write modes
  api/                    # health, metadata, ingestion, admin, dynamic query routes

plugins/
  dcp/
    plugin.yaml           # external collector connector, commands, query routes
    tables.yaml           # 12 DCP business table schemas
    normalizers.py        # 6 normalizers (plan_sgcc_year, plan_progress, plan_dept_key_personnel, line_section, substation, daily_meeting)
    fan_out.py            # project/date fan-out handlers with circuit breaker

scripts/
  dev/                    # 开发调试辅助
  smoke/                  # Smoke 测试脚本
  ops/                    # 运维监控脚本

tests/
  unit/                   # 纯逻辑测试
  integration/            # 集成测试
  e2e/                    # 端到端测试
```

## API

- `GET /health`
- `GET /metadata`
- `GET /plugins`
- `GET /schemas` / `GET /schemas/{table_name}`
- `POST /ingestion/v1/jobs` — 触发采集
- `GET /ingestion/v1/jobs` / `GET /ingestion/v1/jobs/{id}`
- `POST /ingestion/v1/table-batches` — 入库回调
- `GET /ingestion/v1/messages` / `GET /ingestion/v1/table-writes`
- `POST /admin/api-keys`
- Dynamic query routes from plugin `query_routes`

Dev 模式引导 API Key: `dev-admin-key` (scopes: admin, ingestion, query)

## Environment Variables

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATAHUB_DB_PATH` | `data/datahub_mvp.db` | SQLite 数据库路径 |
| `DATAHUB_PLUGIN_DIR` | `plugins` | 插件目录 |
| `DATAHUB_CALLBACK_BASE_URL` | `http://localhost:8000` | 回调基础 URL |
| `DATAHUB_CALLBACK_API_KEY` | dev 模式自动填充 | 回调 API Key，**生产环境必须显式配置** |
| `DATAHUB_DEV_MODE` | `1` | dev 模式开关 |

## Current Limitations

- **8000 ops UI** (`/ops`) 是后续长期运维方向，当前功能有限
- **command → service 抽象尚未开始**，当前 command 直接映射到 trigger
- SQLite 单写者，fan-out 必须串行执行
- DCP session/WAF 过期需手动重启 downloader-dcp
- 部分表未配置 query route（返回 404）
- 无自动重试机制，需通过 CLI 手动 retry

## Documentation

- [MVP_ARCHITECTURE.md](MVP_ARCHITECTURE.md) — 稳定架构设计
- [docs/devlog/dcp-mvp-final-acceptance.md](docs/devlog/dcp-mvp-final-acceptance.md) — MVP 封板验收
- [docs/runbooks/dcp-mvp-smoke-run.md](docs/runbooks/dcp-mvp-smoke-run.md) — Smoke 测试流程
