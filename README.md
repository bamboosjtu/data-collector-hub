# DataCollectorHub MVP

DataCollectorHub 是独立 DataHub 服务。它通过插件声明 schema、trigger 和 query routes，接收标准 TableBatch v1，负责 schema 校验、幂等写入、SQLite 存储、API key 授权和下游查询 API。

`downloader-dcp` 是外部 producer。DataCollectorHub 不实现 DCP 登录、页面抓取、瑞数、加密、分页、Cookie、业务参数派生或 DCP 协议细节。

## Architecture

```text
src/datahub/
  app.py                  # FastAPI app factory and router assembly
  settings.py             # environment-backed settings
  core/                   # plugin loading, registry, trigger runtime
  ingestion/              # TableBatch v1 models, validation, idempotency, service
  storage/                # SQLite DDL, metadata tables, write modes
  api/                    # health, metadata, ingestion, admin, dynamic query routes
  admin/                  # admin UI extension point

plugins/
  dcp/
    plugin.yaml           # external collector connector, commands, query routes
    tables.yaml           # 15 DCP business table schemas

tests/
  phase*.py               # phased verification scripts
  test_phase_scripts.py   # pytest wrapper for phase scripts
```

## Core Responsibilities

- Load plugins from `plugins/*/plugin.yaml`.
- Build a schema registry from `plugins/*/tables.yaml`.
- Trigger external collectors through generic `/sync` calls.
- Receive `POST /ingestion/v1/table-batches`.
- Validate dataset, table, row, scope, primary key, and idempotency rules.
- Write business rows to SQLite using `upsert`, `replace_scope`, or `append`.
- Register query APIs dynamically from plugin `query_routes`.
- Expose health, metadata, ingestion status, table write, and API key APIs.

## DCP Plugin

The DCP plugin is an external collector plugin. It declares commands such as `project_tech_full`, `plan_professional_all`, `year_progress_project_domain`, and `safety_daily_meeting_range`.

DataHub sends:

```json
{
  "job_type": "project_tech_full",
  "params": {"projectCode": "P001"},
  "sink": {
    "type": "http_callback",
    "url": "http://localhost:8000/ingestion/v1/table-batches"
  }
}
```

The external producer later callbacks with TableBatch v1. DataHub owns table schemas and write rules; the producer owns collection, pagination, parameter derivation, and outbox delivery.

## API

Metadata:

- `GET /health`
- `GET /metadata`
- `GET /plugins`
- `GET /schemas`
- `GET /schemas/{table_name}`

Ingestion and status:

- `POST /ingestion/v1/jobs`
- `GET /ingestion/v1/jobs`
- `GET /ingestion/v1/jobs/{ingestion_job_id}`
- `POST /ingestion/v1/table-batches`
- `GET /ingestion/v1/messages`
- `GET /ingestion/v1/messages/{message_id}`
- `GET /ingestion/v1/table-writes`

Admin:

- `POST /admin/api-keys`

Query routes are declared by plugins. The DCP plugin currently registers 15 `/api/v1/...` routes.

The local bootstrap API key is `dev-admin-key` with `admin`, `ingestion`, and `query` scopes.

## Run

```powershell
uv run python run.py
```

The launcher starts:

- FastAPI: `http://localhost:8000`
- Streamlit UI: `http://localhost:8501`

Environment variables:

- `DATAHUB_DB_PATH`
- `DATAHUB_PLUGIN_DIR`
- `DATAHUB_CALLBACK_BASE_URL`

## Verify

Run all phased checks:

```powershell
uv run python tests\phase0_plan.py
uv run python tests\phase1_core_plugin.py
uv run python tests\phase2_dcp_plugin.py
uv run python tests\phase3_storage.py
uv run python tests\phase4_ingestion.py
uv run python tests\phase5_api_runtime.py
uv run python tests\phase6_acceptance.py
```

Run the standard test wrapper:

```powershell
uv run pytest tests -q
```

Compile the migrated package:

```powershell
uv run python -m py_compile src\datahub\__init__.py src\datahub\app.py src\datahub\settings.py src\datahub\core\__init__.py src\datahub\core\errors.py src\datahub\core\plugin_loader.py src\datahub\core\registry.py src\datahub\core\specs.py src\datahub\core\trigger_runtime.py src\datahub\ingestion\__init__.py src\datahub\ingestion\idempotency.py src\datahub\ingestion\models.py src\datahub\ingestion\service.py src\datahub\ingestion\validator.py src\datahub\storage\__init__.py src\datahub\storage\ddl.py src\datahub\storage\sqlite.py src\datahub\storage\writer.py src\datahub\api\__init__.py src\datahub\api\admin.py src\datahub\api\auth.py src\datahub\api\health.py src\datahub\api\ingestion.py src\datahub\api\metadata.py src\datahub\api\query.py
```
