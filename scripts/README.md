# Scripts

DataCollectorHub MVP 只保留可复用的本地运维脚本。一次性分析、旧 schema 验收、旧 fan-out 监控脚本已经移除，避免把历史现场脚本误当作稳定工具。

## 脚本清单

| 脚本 | 用途 | 关键参数 |
|------|------|----------|
| `backup_sqlite.py` | SQLite 在线备份（使用 sqlite3.backup() API） | `--db`, `--out` |
| `mvp_check_env.py` | 环境变量完整性检查 | 无 |
| `mvp_smoke_check.py` | MVP smoke 验证（9 项检查） | `--base-url`, `--api-key` |

```bash
# 备份数据库
python scripts/backup_sqlite.py --db data/datahub_mvp.db --out data/backup.db

# 检查环境变量
python scripts/mvp_check_env.py

# 运行 smoke 验证（需要 DataHub 运行）
python scripts/mvp_smoke_check.py --base-url http://localhost:8000 --api-key dev-admin-key
```

## 已移除脚本类型

- 一次性现场分析脚本：硬编码本机 DB 路径或特定采集窗口，不能作为复用工具
- 旧 schema/旧命令验收脚本：引用已废弃表名、命令名或 fan-out 结果字段
- 复合流程脚本：把触发、等待、验收和停止条件揉在一起，容易与当前调度器能力漂移
- ops/smoke 子目录脚本：功能已收敛到 /ops UI 和上述 3 个脚本
