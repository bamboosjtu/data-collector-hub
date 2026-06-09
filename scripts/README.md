# Scripts

DataCollectorHub 运维与验证脚本，按用途分三个目录。

## 目录结构

```
scripts/
  dev/    # 数据维护工具
  smoke/  # Smoke 测试脚本
  ops/    # 运维监控脚本
```

所有脚本支持 `--help` 查看参数说明。DB 路径和项目根目录通过 `--db` / `--cwd` 参数指定，默认自动检测。

## dev/ — 数据维护

| 脚本 | 用途 | 关键参数 |
|------|------|----------|
| clean_substation.py | 清理 substation 全关键字段为 NULL 的脏数据行 | `--db` |
| verify_30day.py | daily_meeting 验收：行数、extra、主键、日期分布、ingestion 状态 | `--db` |

```bash
# 示例
python scripts/dev/verify_30day.py --db data/datahub_mvp.db
```

## smoke/ — Smoke 测试

| 脚本 | 用途 | 关键参数 |
|------|------|----------|
| verify_daily_full.py | daily_meeting 全流程验证：snapshot → yesterday → 3天范围 → 14天回填 | `--db`, `--cwd` |
| verify_run.py | 通用 job 结果验证：表行数、extra 违规、schema_mismatch、write 错误 | `--db`, `job_id` |

```bash
# 示例
python scripts/smoke/verify_run.py --db data/datahub_mvp.db ing_refresh_annual_plans_current_xxx
```

## ops/ — 运维监控

| 脚本 | 用途 | 关键参数 |
|------|------|----------|
| check_state.py | Hub 状态巡检：表行数、最近 jobs、非终态 jobs、extra 违规 | `--db` |
| check_fanout_detail.py | fan-out 父子任务详情 | `parent_id` |
| full_fanout.py | 执行 fan-out 命令，等待终态，输出前后对比和停止条件检查 | `command`, `--db`, `--cwd` |
| monitor_fanout_v2.py | fan-out 进度实时监控 | `parent_id` |
| wait_fanout.py | 等待 fan-out 终态，输出完整报告（子任务统计、失败详情、表行数） | `parent_id` |
| wait_job.py | 等待单个 job 终态并输出结果 | `job_id` |

```bash
# 示例
python scripts/ops/check_state.py --db data/datahub_mvp.db
python scripts/ops/full_fanout.py refresh_towers_for_current_plan_projects
python scripts/ops/monitor_fanout_v2.py ing_backfill_daily_meetings_by_range_xxx
```
