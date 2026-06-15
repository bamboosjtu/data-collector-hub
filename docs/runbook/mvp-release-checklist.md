# DataHub MVP 发布前验收清单

## 1. Tests

```bash
python -m pytest tests/ -q
```

期望：全部通过，0 failed。

## 2. Schema baseline 验证

确认以下字段存在于 CREATE TABLE 基线中（ddl.py），且无 ALTER TABLE migration：

- [ ] ingestion_jobs.source (TEXT NOT NULL DEFAULT 'api')
- [ ] ingestion_jobs.retry_of_job_id (TEXT)
- [ ] fanout_items.retry_count (INTEGER NOT NULL DEFAULT 0)
- [ ] fanout_items.next_attempt_at (TEXT)
- [ ] scheduled_plans 表
- [ ] scheduled_runs 表
- [ ] scheduled_run_steps 表
- [ ] 零 ALTER TABLE migration 函数

验证命令：
```bash
grep -c "ALTER TABLE" src/datahub/storage/ddl.py
# 期望: 0
```

## 3. P0/P1/P2/P3 集成结论

| 阶段 | 内容 | 结论 |
|------|------|------|
| P0 | JobService / source / retry 状态保护 | PASS |
| P1 | 自动采集计划 / scheduler | PASS |
| P2 | 单 job retry + fan-out failed children retry | PASS |
| P3 | Admin UI 可操作闭环 | PASS |

## 4. Smoke check

```bash
python scripts/mvp_smoke_check.py
```

期望：所有检查 [OK]。

## 5. Backup

```bash
python scripts/backup_sqlite.py
```

期望：输出备份文件路径，文件大小 > 0。

## 6. Rollback 方式

1. 停止 DataHub 服务
2. 还原 SQLite backup: `cp backups/datahub_YYYYMMDD_HHMMSS.sqlite data/datahub_mvp.db`
3. 回退 git commit: `git checkout <commit>`
4. 重启服务

## 7. Known Limitations

- SQLite MVP single-node，不支持多实例并发写入
- Admin UI (/ops) 为最小可用版本，vanilla HTML/CSS/JS
- 不支持 PostgreSQL / Celery / Kafka / RabbitMQ
- DCP 远端失败仍可能产生 partial 状态
- daily schedule 默认关闭，需手动开启
- callback 认证当前为 deferred 模式（无 API Key 时 warn 但放行）
- fanout scheduler 始终运行（当有 connector 时），无独立开关

## 8. Go/No-Go 判断

### Go 条件（全部满足）

- [ ] `python -m pytest tests/ -q` 全部通过
- [ ] `python scripts/mvp_smoke_check.py` 全部 OK
- [ ] 无 schema_mismatch（ddl.py 无 ALTER TABLE）
- [ ] 无 callback 401/403（downloader-dcp 可正常回调）
- [ ] 无 database locked 错误
- [ ] 无 no_connector 错误（downloader-dcp 已启动）
- [ ] recent_days 确认不是 890 天全量回补

### Block 条件（任一出现则 No-Go）

- 测试失败
- Smoke check 失败
- DDL 有 ALTER TABLE
- callback 认证完全不通
- DB 路径不可写
