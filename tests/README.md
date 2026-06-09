# Tests

DataCollectorHub 测试分为三层，由内到外递增依赖。

## 目录结构

```
tests/
  unit/           # 纯逻辑，无外部依赖
  integration/    # 需要 SQLite/Store，不需要外部服务
  e2e/            # 需要完整 DataHub + downloader-dcp 运行
```

## 运行方式

```bash
# 单元测试（随时可跑）
python -m pytest tests/unit/ -v

# 集成测试（需要 SQLite，不需要外部服务）
python -m pytest tests/integration/ -v

# 全量测试（单元 + 集成）
python -m pytest tests/unit/ tests/integration/ -v

# E2E 测试（需要本地 DataHub + downloader-dcp 运行）
python -m pytest tests/e2e/ -v
```

## 测试清单

### unit/

| 文件 | 覆盖能力 |
|------|----------|
| test_validator.py | 空壳行判定、extra 字段过滤、schema 校验 |
| test_normalizer_substation.py | substation normalizer 输出规则 |
| test_normalizer_daily_meeting.py | daily meeting 字段化、date 补全、wrapper 过滤 |
| test_writer_timestamps.py | 业务表 _ingest_created_at/updated_at 写入与 upsert 行为 |

### integration/

| 文件 | 覆盖能力 |
|------|----------|
| test_fan_out_circuit_breaker.py | date/project fan-out 熔断器核心场景 |
| test_plugin_handler.py | plugin handler 前缀校验（防止跨插件加载） |
| test_status_poll.py | downloader 状态轮询、stale 判定、parent 聚合 |

### e2e/

| 文件 | 覆盖能力 |
|------|----------|
| phase1_core_plugin.py | 插件加载、registry 构建、核心代码无 DCP 泄露 |
| phase2_dcp_plugin.py | DCP 插件 connector/命令/表 schema 声明完整性 |
| phase3_storage.py | SQLite 建表、业务表 DDL 与 registry 一致、upsert |
| phase4_ingestion.py | 入库幂等、payload_hash 冲突、idempotency_key 冲突 |
| phase5_api_runtime.py | API 运行时、trigger 命令分发、FakeExternalClient |
| phase6_acceptance.py | 最终验收：核心代码无 DCP 泄露、CLI trigger 端到端 |
| test_phase_scripts.py | 统一执行 phase1-6 的 pytest 入口 |
