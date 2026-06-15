# DataHub MVP 运维手册

## 1. 必需环境变量

| 变量 | 默认值 | 必需 | 说明 |
|------|--------|------|------|
| DATAHUB_DB_PATH | data/datahub_mvp.db | 否 | SQLite 数据库路径 |
| DATAHUB_CALLBACK_BASE_URL | http://localhost:8000 | 否 | 回调基础 URL |
| DATAHUB_CALLBACK_API_KEY | dev 模式自动填充 | 生产必需 | 回调 API Key |
| DATAHUB_DEV_MODE | 1 | 否 | dev 模式开关，生产环境设为 0 |
| DATAHUB_PLUGIN_DIR | plugins | 否 | 插件目录 |
| DATAHUB_COLLECTION_SCHEDULER_ENABLED | (空=false) | 否 | 采集调度器开关 |
| DATAHUB_DAILY_DCP_REFRESH_ENABLED | (空=false) | 否 | 每日 DCP 刷新开关 |
| DATAHUB_DAILY_DCP_REFRESH_TIME | 02:00 | 否 | 每日刷新时间 |
| DATAHUB_DAILY_DCP_RECENT_DAYS | 3 | 否 | 刷新回溯天数 |
| DATAHUB_COLLECTION_SCHEDULER_TICK_SECONDS | 30 | 否 | 调度器 tick 间隔 |

## 2. 推荐 MVP 默认值

- collection_scheduler_enabled: false（手动触发更安全）
- daily_dcp_refresh_enabled: false（确认数据正确后再开启）
- recent_days: 3（不要设为 890，避免全量回补）
- SQLite 路径: 明确指定 DATAHUB_DB_PATH，确保目录存在
- callback_api_key: 生产环境必须显式配置，不能依赖 dev 默认值

## 3. 启动顺序

1. 启动 downloader-dcp: `cd downloader-dcp && uv run python -m downloader_dcp`
2. 启动 data-collector-hub: `python run.py` 或 `python -m uvicorn src.datahub.app:app --host 0.0.0.0 --port 8000`
3. 检查 /health: `curl http://localhost:8000/health`
4. 检查 /health/ready: `curl -H "X-API-Key: dev-admin-key" http://localhost:8000/health/ready`
5. 打开 /ops: 浏览器访问 http://localhost:8000/ops
6. 手动 run smoke plan: 在 /ops Schedules 标签页点击 Run Now
7. 最后再打开 daily schedule: 设置 DATAHUB_COLLECTION_SCHEDULER_ENABLED=1 和 DATAHUB_DAILY_DCP_REFRESH_ENABLED=1

## 4. 健康检查

- GET /health: 基础存活检查，无需认证
- GET /health/ready: 就绪检查，包含 DB 连通性、scheduler 状态等，需要 X-API-Key

## 5. SQLite 备份

```bash
python scripts/backup_sqlite.py
python scripts/backup_sqlite.py --db /path/to/custom.db
```

备份文件输出到 backups/ 目录。建议在以下时机手动备份：
- 升级前
- 开启 daily schedule 前
- 大规模 fan-out 操作前

## 6. 日常采集计划开关

- 默认关闭：DATAHUB_COLLECTION_SCHEDULER_ENABLED 不设置
- 开启：设置 DATAHUB_COLLECTION_SCHEDULER_ENABLED=1
- daily_dcp_refresh 默认关闭，开启需同时设置 DATAHUB_DAILY_DCP_REFRESH_ENABLED=1
- 重要：recent_days 不要设为 890，避免全量回补

## 7. 环境检查

```bash
python scripts/mvp_check_env.py
```

## 8. Smoke 检查

```bash
python scripts/mvp_smoke_check.py
python scripts/mvp_smoke_check.py --run-plan p1_smoke_plan
```

## 9. 常见问题

### database locked
- 原因：SQLite 并发写入冲突
- 处理：检查是否有多个进程写入同一 DB

### callback 401/403
- 原因：DATAHUB_CALLBACK_API_KEY 未配置或不匹配
- 处理：确认 downloader-dcp 侧的 API key 与 DataHub 一致

### no_connector
- 原因：downloader-dcp 未启动或 connector URL 不正确
- 处理：检查 downloader-dcp 运行状态和 plugin.yaml 中的 connector.base_url

### fanout partial
- 原因：部分子任务失败
- 处理：在 /ops Fan-out 标签页查看详情，使用 Retry Failed Children

### daily schedule 误触发 890 天回补
- 预防：确认 DATAHUB_DAILY_DCP_RECENT_DAYS=3，不要设为 890
- 处理：立即停止服务，还原 SQLite backup

## 10. 回滚方式

1. 停止 DataHub 服务
2. 还原 SQLite backup: `cp backups/datahub_YYYYMMDD_HHMMSS.sqlite data/datahub_mvp.db`
3. 回退 git commit: `git checkout <commit>`
4. 重启服务
