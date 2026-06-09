# Tests

DataCollectorHub MVP 的维护测试面收敛为 `unit` 和 `integration`。旧 `e2e/phase1-6` 阶段脚本绑定早期 DCP 表名、命令名和验收口径，已经删除；真实 downloader-dcp 联调不再通过这些过期 pytest 脚本表达。

## 目录结构

```text
tests/
  unit/         # 纯逻辑测试，无外部服务依赖
  integration/  # SQLite/Store/API 运行时边界测试，不依赖 downloader-dcp 服务
```

## 运行方式

```bash
# 当前维护的完整测试套件
uv run pytest tests/unit tests/integration -q

# 单元测试
uv run pytest tests/unit -q

# 集成测试
uv run pytest tests/integration -q

# 重点回归：并发 fan-out + 状态轮询
uv run pytest tests/integration/test_fan_out_circuit_breaker.py tests/integration/test_status_poll.py -q
```

## 测试清单

### unit/

| 文件 | 覆盖能力 |
|------|----------|
| `test_validator.py` | 空壳行判定、extra 字段过滤、schema 校验 |
| `test_normalizer_substation.py` | substation normalizer 输出规则 |
| `test_normalizer_daily_meeting.py` | daily meeting 字段化、date 补全、wrapper 过滤 |
| `test_writer_timestamps.py` | 业务表 `_ingest_created_at`/`_ingest_updated_at` 写入与 upsert 行为 |

### integration/

| 文件 | 覆盖能力 |
|------|----------|
| `test_fan_out_circuit_breaker.py` | fan-out scheduler、SQLite fanout store、并发 claim、熔断/恢复、父任务聚合边界 |
| `test_plugin_handler.py` | plugin handler 前缀校验，防止跨插件加载 |
| `test_status_poll.py` | downloader 状态轮询、stale 判定、parent/child job 聚合 |

## E2E 策略

旧 `tests/e2e` 套件已经移除，因为它验证的是历史表结构和历史命令，不再代表当前 MVP 正确性。需要做真实 downloader-dcp 验收时，应使用明确的人工验收步骤或新增面向当前 schema/命令的测试，且不要复用已废弃的 phase 脚本口径。