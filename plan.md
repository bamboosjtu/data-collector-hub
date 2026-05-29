# DataCollectorHub MVP Full Migration With DCP Plugin

## Summary

按 `MVP_ARCHITECTURE.md` 和 `DCP_INTEGRATION.md` 完整迁移。先落盘 `plan.md`，再分阶段实现；每阶段完成后新增 `tests/phase*.py` 验证脚本，运行通过后更新 `plan.md` 状态。DCP 必须作为 `plugins/dcp` external collector plugin 接入，DataHub 只声明 schema、trigger、query routes，并通过 `/sync` 触发 downloader-dcp，不实现任何 DCP 采集、登录、参数派生或协议逻辑。

## Phase Plan

| Phase | Goal | Verification |
|---|---|---|
| Phase 0 | 创建 `plan.md` 和 `tests/` 阶段脚本框架 | `uv run python tests/phase0_plan.py` |
| Phase 1 | 迁移 core/plugin/registry 骨架 | `uv run python tests/phase1_core_plugin.py` |
| Phase 2 | 编写并验证 DCP 插件 | `uv run python tests/phase2_dcp_plugin.py` |
| Phase 3 | 迁移 SQLite storage/write modes | `uv run python tests/phase3_storage.py` |
| Phase 4 | 迁移 TableBatch ingestion/idempotency | `uv run python tests/phase4_ingestion.py` |
| Phase 5 | 实现 trigger/query/admin API | `uv run python tests/phase5_api_runtime.py` |
| Phase 6 | 清理旧代码并做最终验收 | `uv run python tests/phase6_acceptance.py` |

`plan.md` 每阶段状态为 `pending`、`in_progress`、`done` 或 `failed`，并记录实际验证命令与结果。

## Key Implementation Changes

- 重建包结构：`src/datahub/core/`、`src/datahub/ingestion/`、`src/datahub/storage/`、`src/datahub/api/`、`src/datahub/admin/`。
- 删除旧兼容入口和不符合目标架构的正式路径，不保留 `api.server` 兼容依赖。
- `src/datahub/app.py` 只做 app factory 和 router 装配。
- `core/trigger_runtime.py` 实现通用 external collector trigger：读取 plugin connector/command，POST `/sync`，注入 `sink.url=/ingestion/v1/table-batches`。
- DCP 插件位于 `plugins/dcp/`，包含 `plugin.yaml` 和 `tables.yaml`：
  - 声明 connector：`type: downloader_sync`、`base_url`、`timeout_seconds`。
  - 声明 commands/job_type：`project_tech_full`、`daily_meeting_today_snapshot`、`daily_meeting_yesterday_final`、`plan_professional_all`、`year_progress_project_domain`、`safety_daily_meeting_range`。
  - 声明 required params：如 `projectCode`、`date`、`planYear`、`year`、`startDate/endDate`。
  - 声明 15 张 MVP 业务表、write mode、primary key、scope columns、registered columns、`extra` json。
  - 声明 query routes，由 core 动态注册。
- DataHub 不处理 downloader-dcp outbox 内部状态，只保证 callback 下游契约：成功幂等返回 2xx，schema mismatch 返回非 2xx。
- `scripts/integration_collect_dcp.py` 不能作为正式路径保留；删除或迁移为明确的废弃参考，不得导入 `DcpApiClient`。

## DCP Plugin Validation

`tests/phase2_dcp_plugin.py` 必须验证：

- `plugins/dcp/plugin.yaml` 和 `tables.yaml` 可加载。
- DCP plugin 声明 external collector connector，不包含 DCP 登录、cookie、瑞数、分页、参数派生。
- 所有 DCP query routes 指向已注册表。
- 所有 command required params 与 `DCP_INTEGRATION.md` sync 请求模式一致。
- 15 张 MVP 表存在，且 `dcp_year_progress_project_domain` 使用 `replace_scope`，主要计划/安全表使用 `upsert`。
- 插件 schema 拒绝未知列；未注册字段只允许进入声明的 `extra` json 列。
- 删除或禁用 `plugins/dcp` 后 core 仍能启动。

## TableBatch And API Contract

- 入库入口只保留 `POST /ingestion/v1/table-batches`。
- TableBatch v1 字段保持：`message_id`、`idempotency_key`、`downloader_job_id`、`collect_run_id`、`dataset_key`、`scope_key`、`payload_hash`、`tables[]`。
- 幂等规则：
  - 同 `message_id` + 同 `payload_hash` 返回 `duplicate_accepted` 和 2xx。
  - 同 `message_id` + 不同 `payload_hash` 返回 `payload_hash_conflict` 和 409。
  - 同 `idempotency_key` + 不同 `message_id` 返回 `idempotency_conflict` 和 409。
  - schema mismatch 返回非 2xx，允许 downloader outbox 后续重试。
- 查询 API 只返回注册业务 DTO，不返回 `_ingest_*`、raw DCP 记录或协议字段。

## Test Plan

- `phase0_plan.py`：检查 `plan.md` 阶段表和 `tests/` 结构。
- `phase1_core_plugin.py`：验证 core 包结构、plugin loader、registry、空 plugin 目录启动能力。
- `phase2_dcp_plugin.py`：验证 DCP plugin 声明完整性、边界清洁、表和 query routes。
- `phase3_storage.py`：验证元数据表、业务表 DDL、upsert、replace_scope、append。
- `phase4_ingestion.py`：验证 TableBatch validator、dataset/table mismatch、schema mismatch、幂等冲突。
- `phase5_api_runtime.py`：验证 FastAPI routers、API key scopes、动态 query routes、fake `/sync` trigger payload。
- `phase6_acceptance.py`：扫描 core 无 `dcp_sdk`、`DcpApiClient`、`pageName`、`apiName`、`cookie`、`session`、`瑞数`；运行全部阶段脚本和 `uv run pytest tests -q`。

## Assumptions

- `downloader_job_id` 字段名保留，因为它是 TableBatch v1 与 downloader-dcp sync 集成契约的一部分，不代表 core 依赖 downloader 内部实现。
- DCP 账号池、outbox、dispatcher、分页、前置请求、参数派生全部属于 downloader-dcp，不在 DataCollectorHub 实现。
- DataHub 只触发 `/sync`、接收 callback、幂等写库、提供查询和排查 API。
