# Data Collector Hub - 运维文档

---

## 1. 环境要求

### 1.1 系统依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 运行环境 |
| SQLite | 3.35+ | 数据存储 |
| pip | 最新 | 包管理 |

### 1.2 Python 依赖包

```
fastapi>=0.104.0
uvicorn>=0.24.0
apscheduler>=3.10.0
pydantic>=2.5.0
websockets>=12.0
feedparser>=6.0.0
requests>=2.31.0
python-multipart>=0.0.6
```

---

## 2. 安装部署

### 2.1 安装步骤

```bash
# 1. 克隆仓库
git clone <repository-url>
cd DataCollectorHub

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 初始化数据库
python -c "from storage.sqlite_store import SQLiteStore; store = SQLiteStore(); store.init_db()"

# 6. 启动服务
python main.py
```

### 2.2 目录结构

```
DataCollectorHub/
├── api/                    # API接口层
│   ├── server.py           # REST API / Ingestion API / Processing API / Sandbox API
│   ├── rss_feed.py         # RSS Feed生成
│   ├── websocket.py        # WebSocket服务
│   └── mcp_server.py       # MCP Server接口
├── core/                   # 核心逻辑层
│   ├── base_adapter.py     # 插件基类
│   ├── plugin_manager.py   # 插件管理
│   └── scheduler.py        # 任务调度
├── processing/             # 数据处理层
│   └── normalizer_runner.py # 归一化处理器
├── plugins/                # 插件目录
│   ├── rss_news.py         # RSS新闻插件
│   ├── demo_plugin.py      # 演示插件
│   └── dcp.py              # DCP外部采集器控制插件
├── storage/                # 数据存储层
│   └── sqlite_store.py     # SQLite存储实现
├── dashboard/              # 管理界面
│   └── streamlit_app.py    # Streamlit管理面板
├── doc/                    # 文档目录
├── data/                   # 数据文件目录（自动创建）
│   └── data_collector.db   # SQLite数据库
├── main.py                 # 主入口
├── requirements.txt        # 依赖列表
└── README.md               # 项目说明
```

---

## 3. 配置管理

### 3.1 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DCH_HOST` | `0.0.0.0` | 服务监听地址 |
| `DCH_PORT` | `8000` | 服务端口 |
| `DCH_DB_PATH` | `data/data_collector.db` | 数据库路径 |
| `DCH_LOG_LEVEL` | `INFO` | 日志级别 |
| `DCH_PLUGIN_DIR` | `plugins` | 插件目录 |
| `DCH_SCHEDULER_ENABLED` | `true` | 是否启用调度器 |

### 3.2 配置文件

```python
# config.py（示例）
import os

class Config:
    HOST = os.getenv("DCH_HOST", "0.0.0.0")
    PORT = int(os.getenv("DCH_PORT", 8000))
    DB_PATH = os.getenv("DCH_DB_PATH", "data/data_collector.db")
    LOG_LEVEL = os.getenv("DCH_LOG_LEVEL", "INFO")
    PLUGIN_DIR = os.getenv("DCH_PLUGIN_DIR", "plugins")
    SCHEDULER_ENABLED = os.getenv("DCH_SCHEDULER_ENABLED", "true").lower() == "true"
```

---

## 4. 启动与停止

### 4.1 启动服务

```bash
# 前台启动
python main.py

# 后台启动（Linux）
nohup python main.py > logs/dch.log 2>&1 &

# 使用 uvicorn 直接启动
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 4.2 停止服务

```bash
# 查找进程并停止
ps aux | grep "python main.py"
kill <pid>

# 或强制停止
kill -9 <pid>
```

### 4.3 服务状态检查

```bash
# 检查端口
netstat -tlnp | grep 8000

# 或
curl http://localhost:8000/api/stats
```

---

## 5. 监控与告警

### 5.1 关键指标

| 指标 | 查询方式 | 告警阈值 |
|------|----------|----------|
| 插件运行次数 | `task_stats.run_count` | - |
| 插件失败次数 | `task_stats.fail_count` | > 3 |
| 连续失败次数 | `task_stats.consecutive_fails` | > 3 |
| 原始数据量 | `raw_data` 行数 | - |
| 规范化数据量 | `normalized_data` 行数 | - |
| 上游事件量 | `raw_events` 行数 | - |
| 实体数据量 | `canonical_entities` 行数 | - |
| WebSocket连接数 | `/ws/stats` | - |

### 5.2 健康检查

```bash
# 插件健康检查
curl http://localhost:8000/api/plugins

# 系统统计
curl http://localhost:8000/api/stats

# WebSocket状态
curl http://localhost:8000/ws/stats
```

### 5.3 日志查看

```bash
# 查看实时日志
tail -f logs/dch.log

# 查看错误日志
grep "ERROR" logs/dch.log

# 查看特定插件日志
sqlite3 data/data_collector.db "SELECT * FROM logs WHERE plugin_id='rss_news' ORDER BY created_at DESC LIMIT 10;"
```

---

## 6. 数据备份与恢复

### 6.1 备份策略

```bash
# 全量备份
cp data/data_collector.db backups/data_collector_$(date +%Y%m%d_%H%M%S).db

# 定时备份（crontab）
# 每天凌晨2点备份
0 2 * * * cp /path/to/data/data_collector.db /path/to/backups/data_collector_$(date +\%Y\%m\%d).db
```

### 6.2 数据导出

```bash
# 导出为SQL
sqlite3 data/data_collector.db ".dump" > backup.sql

# 导出特定表
sqlite3 data/data_collector.db ".dump raw_data" > raw_data.sql
sqlite3 data/data_collector.db ".dump raw_events" > raw_events.sql
sqlite3 data/data_collector.db ".dump canonical_entities" > canonical_entities.sql
```

### 6.3 数据恢复

```bash
# 从备份恢复
cp backups/data_collector_20260322.db data/data_collector.db

# 从SQL恢复
sqlite3 data/data_collector.db < backup.sql
```

---

## 7. 插件管理

### 7.1 查看插件列表

```bash
curl http://localhost:8000/api/plugins
```

### 7.2 启用/禁用插件

```bash
# 禁用插件
curl -X PUT http://localhost:8000/api/plugins/rss_news/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# 启用插件
curl -X PUT http://localhost:8000/api/plugins/rss_news/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 7.3 手动触发插件

```bash
curl -X POST http://localhost:8000/api/plugins/rss_news/trigger \
  -H "Content-Type: application/json" \
  -d '{"config": {"feed_url": "https://example.com/feed.xml"}}'
```

### 7.4 更新插件配置

```bash
curl -X PUT http://localhost:8000/api/plugins/rss_news/config \
  -H "Content-Type: application/json" \
  -d '{"feed_url": "https://new-example.com/feed.xml"}'
```

---

## 8. 上游数据接入运维

### 8.1 Ingestion API 监控

```bash
# 查看最近接入的上游事件
sqlite3 data/data_collector.db "SELECT source_system, source_event_type, dataset_key, COUNT(*) FROM raw_events GROUP BY source_system, dataset_key;"

# 查看特定数据集的事件
sqlite3 data/data_collector.db "SELECT * FROM raw_events WHERE dataset_key='dcp.daily_meeting' ORDER BY created_at DESC LIMIT 10;"
```

### 8.2 幂等性检查

```bash
# 检查重复事件
sqlite3 data/data_collector.db "SELECT idempotency_key, COUNT(*) as cnt FROM raw_events GROUP BY idempotency_key HAVING cnt > 1;"
```

### 8.3 上游系统接入状态

| 检查项 | 命令/查询 |
|--------|-----------|
| 接入事件总数 | `SELECT COUNT(*) FROM raw_events;` |
| 各系统接入量 | `SELECT source_system, COUNT(*) FROM raw_events GROUP BY source_system;` |
| 最近接入时间 | `SELECT MAX(collected_at) FROM raw_events;` |
| 异常事件 | `SELECT * FROM raw_events WHERE payload IS NULL;` |

---

## 9. 归一化处理运维

### 9.1 Normalizer 状态检查

```bash
# 查看各数据集处理进度
sqlite3 data/data_collector.db "SELECT * FROM normalizer_state;"

# 查看处理作业状态
sqlite3 data/data_collector.db "SELECT * FROM processing_jobs ORDER BY created_at DESC LIMIT 10;"
```

### 9.2 手动触发归一化

```bash
# 前台运行
curl -X POST http://localhost:8000/processing/v1/run \
  -H "Content-Type: application/json" \
  -d '{"dataset_key": "dcp.daily_meeting", "mode": "incremental", "batch_size": 1000}'

# 提交后台作业
curl -X POST http://localhost:8000/processing/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"dataset_key": "dcp.daily_meeting", "mode": "incremental", "batch_size": 1000}'

# 查询作业状态
curl http://localhost:8000/processing/v1/jobs/job_abc123
```

### 9.3 归一化监控指标

| 指标 | 查询方式 |
|------|----------|
| 待处理事件数 | `SELECT COUNT(*) FROM raw_events WHERE id > (SELECT last_raw_event_id FROM normalizer_state WHERE dataset_key='xxx');` |
| 实体数据量 | `SELECT entity_type, COUNT(*) FROM canonical_entities GROUP BY entity_type;` |
| 处理成功率 | `SELECT status, COUNT(*) FROM processing_jobs GROUP BY status;` |

---

## 10. 下游应用接口运维

### 10.1 Sandbox API 检查

```bash
# 检查可用日期
curl http://localhost:8000/api/v1/sandbox/dates

# 检查地图骨架
curl http://localhost:8000/api/v1/sandbox/map/skeleton

# 检查地图汇总
curl http://localhost:8000/api/v1/sandbox/map/summary?date=2026-05-01
```

### 10.2 下游数据质量检查

```bash
# 检查实体数据完整性
sqlite3 data/data_collector.db "SELECT entity_type, COUNT(*) as cnt, COUNT(attributes) as attr_cnt FROM canonical_entities GROUP BY entity_type;"

# 检查缺失属性的实体
sqlite3 data/data_collector.db "SELECT entity_type, entity_key FROM canonical_entities WHERE attributes IS NULL OR attributes='{}';"
```

---

## 11. 常见问题处理

### 11.1 插件采集失败

**症状**：`task_stats.fail_count` 增加

**排查步骤**：
1. 查看插件日志：`SELECT * FROM logs WHERE plugin_id='xxx' ORDER BY created_at DESC;`
2. 检查插件配置：`SELECT config FROM plugins WHERE id='xxx';`
3. 手动触发测试：`curl -X POST /api/plugins/xxx/trigger`
4. 检查数据源可用性

**解决方案**：
- 网络问题：检查网络连接，配置代理
- 配置错误：更新插件配置
- 数据源变更：更新插件代码

### 11.2 数据库锁定

**症状**：`sqlite3.OperationalError: database is locked`

**原因**：SQLite 不支持高并发写入

**解决方案**：
1. 减少并发写入
2. 使用连接池
3. 考虑迁移到 PostgreSQL（生产环境建议）

### 11.3 内存溢出

**症状**：服务崩溃，日志显示 `MemoryError`

**原因**：单次采集数据量过大

**解决方案**：
1. 限制单次采集数量
2. 分批处理
3. 增加系统内存

### 11.4 上游事件重复

**症状**：`raw_events` 中出现重复 `idempotency_key`

**排查**：
```bash
sqlite3 data/data_collector.db "SELECT idempotency_key, COUNT(*) as cnt FROM raw_events GROUP BY idempotency_key HAVING cnt > 1;"
```

**解决方案**：
- 检查上游系统是否正确生成 `idempotency_key`
- 确认数据库唯一约束正常工作

### 11.5 归一化处理失败

**症状**：`processing_jobs` 中状态为 `failed`

**排查步骤**：
1. 查看错误信息：`SELECT error FROM processing_jobs WHERE job_id='xxx';`
2. 检查 raw_events 数据格式
3. 检查 normalizer 配置

---

## 12. 性能优化

### 12.1 数据库优化

```sql
-- 分析表（更新统计信息）
ANALYZE;

-- 重建索引
REINDEX;

-- 清理碎片
VACUUM;
```

### 12.2 查询优化

```sql
-- 添加常用查询索引
CREATE INDEX IF NOT EXISTS idx_raw_events_time ON raw_events(collected_at);
CREATE INDEX IF NOT EXISTS idx_canonical_entities_type ON canonical_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_canonical_entities_dataset ON canonical_entities(dataset_key);
```

### 12.3 批量处理

```python
# 批量插入（比单条插入快10倍+）
def batch_insert(items, batch_size=1000):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        insert_many(batch)
```

---

## 13. 升级维护

### 13.1 版本升级

```bash
# 1. 备份数据
cp data/data_collector.db backups/data_collector_$(date +%Y%m%d).db

# 2. 拉取新版本
git pull origin main

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 数据库迁移（如有）
python scripts/migrate.py

# 5. 重启服务
kill <pid>
python main.py
```

### 13.2 数据库迁移

```python
# migrate.py（示例）
def migrate_v1_to_v2():
    """v1 -> v2 迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 添加新列
    cursor.execute("ALTER TABLE plugins ADD COLUMN plugin_kind TEXT DEFAULT 'embedded'")
    cursor.execute("ALTER TABLE plugins ADD COLUMN execution_mode TEXT DEFAULT 'embedded_pipeline'")

    # 创建新表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_events (
            ...
        )
    """)

    conn.commit()
    conn.close()
```

---

## 14. 安全建议

### 14.1 访问控制

- 生产环境使用反向代理（Nginx）
- 配置防火墙规则
- 使用 HTTPS

### 14.2 数据安全

- 定期备份数据库
- 敏感数据加密存储
- 限制数据库文件权限

### 14.3 日志安全

- 避免在日志中记录敏感信息
- 定期清理日志文件
- 配置日志轮转

---

*文档版本: v1.1*
*最后更新: 2026-05-06*
