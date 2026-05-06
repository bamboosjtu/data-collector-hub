# Data Collector Hub v1.0 功能清单

> 生成时间: 2026-05-06
> 版本: v1.1

---

## 核心架构 (Core)

### 1. Plugin Discovery (插件发现)
- [x] 基于 AST 的懒加载插件发现
- [x] 无需导入即可提取元数据
- [x] 支持 `_base/` 目录排除
- [x] 插件元数据：id, name, version, description, author, tags, config_schema
- [x] 插件类型区分：`plugin_kind`（embedded/external）
- [x] 执行模式区分：`execution_mode`（embedded_pipeline/external_job）

**文件**: `core/plugin_manager.py`

### 2. Base Adapter (基础适配器)
- [x] `DataItem` 数据模型
- [x] `BaseAdapter` 抽象基类
- [x] `fetch()` 抽象方法（必须实现）
- [x] `normalize()` 可选方法
- [x] `health_check()` 可选方法
- [x] 支持嵌入式采集和外部采集器控制两种模式

**文件**: `core/base_adapter.py`

### 3. Data Pipeline (数据管道)
- [x] raw_data 存储（插件采集原始数据）
- [x] normalize 处理
- [x] unique_key 生成（MD5 哈希）
- [x] normalized_data 存储（插件规范化数据）
- [x] 增量采集状态管理（plugin_state）
- [x] 重复数据检测（基于 unique_key）

**文件**: `core/pipeline.py`

### 4. Task Scheduler (任务调度器)
- [x] APScheduler 集成
- [x] 并发控制（Semaphore）
- [x] 任务超时保护
- [x] 跳过禁用插件
- [x] 失败统计更新
- [x] 日志记录
- [x] 手动触发支持

**文件**: `core/scheduler.py`

### 5. WebSocket Broadcast Manager
- [x] Single-poll broadcast 架构
- [x] 多客户端连接管理
- [x] 客户端过滤（plugins, interval）
- [x] 统计信息（polling_task_count, client_count 等）
- [x] 无新数据不重复推送

**文件**: `core/websocket_manager.py`

### 6. MCP Tools (LLM 工具接口)
- [x] `list_plugins` 工具
- [x] `query_data` 工具
- [x] `trigger_plugin` 工具
- [x] 工具模式定义（TOOL_SCHEMAS）
- [x] 复用现有服务（无独立业务逻辑）

**文件**: `core/mcp_tools.py`

---

## 数据处理层 (Processing)

### 7. Normalizer Runner (归一化处理器)
- [x] 增量归一化处理（基于 normalizer_state）
- [x] 数据集路由（dataset_key → normalizer）
- [x] raw_events → canonical_entities 转换
- [x] UPSERT 语义（entity_type + entity_key 唯一）
- [x] 前台同步处理和后台异步作业两种模式
- [x] 处理作业状态追踪（processing_jobs）
- [x] Monitor 数据集专用归一化

**文件**: `processing/normalizer_runner.py`

---

## 存储层 (Storage)

### SQLite Store
- [x] 数据库初始化（init_schema）
- [x] 线程安全（per-operation connections）
- [x] 表结构：
  - plugins / plugin_tags / plugin_runtime_configs
  - raw_data（插件采集原始数据）
  - raw_events（上游系统推送的标准化 SourceEvent）
  - normalized_data（插件规范化数据）
  - canonical_entities（归一化实体数据，面向下游应用）
  - normalizer_state（归一化处理进度）
  - processing_jobs（处理作业状态）
  - task_stats
  - plugin_state
  - logs
- [x] CRUD 操作
- [x] JSON 文本存储

**文件**: `storage/sqlite_store.py`

---

## API 层 (API)

### REST API
- [x] `GET /api/plugins` - 插件列表
- [x] `GET /api/plugins/{plugin_id}/config` - 获取插件配置
- [x] `PUT /api/plugins/{plugin_id}/config` - 更新插件配置
- [x] `POST /api/plugins/{plugin_id}/trigger` - 触发插件
- [x] `GET /api/data` - 查询 raw_data
- [x] `GET /api/data/normalized` - 查询 normalized_data
- [x] `GET /api/stats` - 系统统计

### Ingestion API（上游数据接入）
- [x] `POST /ingestion/v1/events` - 批量接入 SourceEvent
- [x] SourceEvent 格式校验
- [x] 幂等性保证（idempotency_key）
- [x] 支持多上游系统（source_system 标识）

### Processing API（归一化处理）
- [x] `POST /processing/v1/run` - 前台运行归一化
- [x] `POST /processing/v1/jobs` - 提交后台归一化作业
- [x] `GET /processing/v1/jobs/{job_id}` - 查询作业状态
- [x] `POST /processing/v1/run-monitor` - 运行 Monitor 数据集归一化
- [x] 支持增量和全量两种模式

### Sandbox API（下游应用接口）
- [x] `GET /api/v1/sandbox/dates` - 获取可用日期列表
- [x] `GET /api/v1/sandbox/map/skeleton` - 获取地图骨架数据
- [x] `GET /api/v1/sandbox/map/summary` - 获取地图汇总数据
- [x] 数据隔离：返回标准化 DTO，不暴露原始 DCP 字段

### RSS Feed
- [x] `GET /feed/rss` - RSS 2.0 输出
- [x] 支持 tag 过滤
- [x] 支持 limit 参数
- [x] 标准 RSS 字段（title, link, description, pubDate, guid）

### WebSocket
- [x] `GET /ws/stream` - WebSocket 连接
- [x] `GET /ws/stats` - 连接统计
- [x] 客户端过滤配置
- [x] 实时数据推送

### MCP
- [x] `GET /mcp` - 工具发现
- [x] `POST /mcp/call` - 工具调用

**文件**: `api/server.py`, `api/rss_feed.py`, `api/websocket.py`, `api/mcp_server.py`

---

## 插件 (Plugins)

### RSS News Plugin (默认插件)
- [x] 中国新闻网 RSS 采集
- [x] fetch() 实现
- [x] normalize() 实现
- [x] 增量采集支持
- [x] plugin_kind = embedded

**文件**: `plugins/rss_news.py`

### DCP External Collector Plugin
- [x] DCP 外部采集器控制
- [x] fetch() 触发外部采集
- [x] 数据由 DCP 通过 Ingestion API 推送
- [x] plugin_kind = external
- [x] execution_mode = external_job

**文件**: `plugins/dcp.py`

### Demo/Test Plugins
- [x] demo_plugin - 基础示例
- [x] failing_plugin - 失败测试
- [x] slow_plugin - 超时测试

---

## 测试与验证

### 集成测试
- [x] `test_integration_rc1.py` - RC-1 集成验收测试
- [x] 覆盖所有核心模块
- [x] 自动化验证脚本

### WebSocket 专项测试
- [x] `test_websocket_verification.py` - WebSocket 收口验证
- [x] 验证 single-poll 架构

---

## 文档

- [x] `README.md` - 项目说明
- [x] `.trae/rules/project-rules.md` - 项目规则
- [x] `AGENTS.md` - Agent 指南
- [x] `doc/01-overview.md` - 总览文档
- [x] `doc/02-prd.md` - PRD 文档
- [x] `doc/03-architecture.md` - 架构文档
- [x] `doc/04-data-model.md` - 数据模型文档
- [x] `doc/05-api-spec.md` - API 规范文档
- [x] `doc/06-plugin-dev-guide.md` - 插件开发指南
- [x] `doc/07-operations.md` - 运维文档

---

## v1.0 设计约束（已实现）

| 约束 | 状态 |
|-----|------|
| 单节点部署 | ✅ |
| SQLite 唯一存储 | ✅ |
| 无认证/权限系统 | ✅ |
| 协程级隔离 | ✅ |
| 无分布式调度 | ✅ |
| 无进程级沙箱 | ✅ |
| 无事件驱动流 | ✅ |
| 无插件依赖图 | ✅ |

---

## 数据流验证

### 插件采集数据流
```
plugin fetch()
    ↓
save to raw_data
    ↓
normalize() [optional]
    ↓
pipeline unique_key generation
    ↓
save to normalized_data
    ↓
update plugin_state [if incremental]
    ↓
update task_stats
    ↓
write logs
```

### 上游接入数据流
```
upstream system (e.g., DCP)
    ↓
POST /ingestion/v1/events (SourceEvent)
    ↓
save to raw_events
    ↓
Normalizer processing
    ↓
save to canonical_entities (UPSERT)
    ↓
update normalizer_state
    ↓
downstream app (e.g., Sandbox) queries via Sandbox API
```

✅ 数据流完整实现

---

## 接口协议支持

| 协议 | 状态 | 说明 |
|-----|------|------|
| REST | ✅ | 主要集成接口 |
| Ingestion | ✅ | 上游数据接入 |
| Processing | ✅ | 归一化处理 |
| Sandbox | ✅ | 下游应用接口 |
| RSS | ✅ | 只读订阅输出 |
| WebSocket | ✅ | 单轮询广播 |
| MCP | ✅ | LLM 工具接口 |

---

## 统计

- **核心模块**: 7 个
- **API 端点**: 18+ 个
- **MCP 工具**: 3 个
- **插件**: 4 个（2 个生产 + 2 个测试）
- **数据库表**: 11 个
- **测试脚本**: 2 个
- **文档**: 10 份

---

## 已知限制（设计内）

1. **单节点**: 不支持分布式部署
2. **SQLite**: 不支持 PostgreSQL/MySQL
3. **无认证**: 无用户/权限系统
4. **弱 schema**: normalized_data / canonical_entities 为半结构化
5. **无插件依赖**: 插件间无法相互调用
6. **日志仅本地**: 无远程日志收集

以上限制均为 v1.0 设计约束，非缺陷。
