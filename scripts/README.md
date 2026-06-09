# Scripts

DataCollectorHub MVP 只保留可复用的本地运维与结果核验脚本。一次性分析、旧 schema 验收、旧 fan-out 监控脚本已经移除，避免把历史现场脚本误当作稳定工具。

## 目录结构

```text
scripts/
  ops/    # 本地运维和 job/fan-out 状态查看
  smoke/  # 单次运行后的轻量结果核验
```

## ops/ - 本地运维

| 脚本 | 用途 | 关键参数 |
|------|------|----------|
| `check_state.py` | 查看业务表行数、最近 jobs、非终态 jobs、extra 违规 | `--db` |
| `check_fanout_detail.py` | 通过本地 API 查看 fan-out 父任务和子任务摘要 | `parent_id` |
| `wait_fanout.py` | 等待 fan-out 父任务终态，并输出子任务统计、失败详情、关键表行数 | `parent_job_id`, `--db`, `--base-url`, `--api-key`, `--timeout` |
| `wait_job.py` | 等待单个 ingestion job 终态并输出结果摘要 | `job_id` |

```bash
python scripts/ops/check_state.py --db data/datahub_mvp.db
python scripts/ops/wait_job.py ing_refresh_annual_plans_current_xxx
python scripts/ops/wait_fanout.py ing_backfill_daily_meetings_by_range_xxx --db data/datahub_mvp.db
python scripts/ops/check_fanout_detail.py ing_backfill_daily_meetings_by_range_xxx
```

说明：`check_fanout_detail.py` 和 `wait_job.py` 面向本地 MVP 默认环境，默认 API 为 `http://localhost:8000`，API key 为 `dev-admin-key`。

## smoke/ - 结果核验

| 脚本 | 用途 | 关键参数 |
|------|------|----------|
| `verify_run.py` | 核验一次 job 的业务表行数、消息、table_writes、extra 违规、schema_mismatch 和写入错误 | `--db`, `job_id` |

```bash
python scripts/smoke/verify_run.py --db data/datahub_mvp.db ing_refresh_annual_plans_current_xxx
```

## 已移除脚本类型

- 一次性现场分析脚本：硬编码本机 DB 路径或特定采集窗口，不能作为复用工具。
- 旧 schema/旧命令验收脚本：引用已废弃表名、命令名或 fan-out 结果字段。
- 复合流程脚本：把触发、等待、验收和停止条件揉在一起，容易与当前调度器能力漂移；需要时优先组合 CLI、`wait_job.py`/`wait_fanout.py` 和 `verify_run.py`。