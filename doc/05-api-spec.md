# Data Collector Hub - API 接口规范

---

## 1. 接口概览

| 协议 | 用途 | 路径前缀 |
|------|------|----------|
| REST API | 结构化数据查询、管理操作 | `/api/*` |
| Ingestion API | 上游系统数据接入 | `/ingestion/*` |
| Processing API | 归一化处理 | `/processing/*` |
| Sandbox API | 下游应用专用接口 | `/api/v1/sandbox/*` |
| RSS Feed | 订阅推送、自动化流程 | `/feed/*` |
| WebSocket | 准实时流推送 | `/ws/*` |
| MCP Server | LLM工具调用接口 | `/mcp` |

---

## 2. API 稳定性声明

> ⚠️ **当前为 MVP 版本**
>
> 本 API 文档处于项目早期阶段（MVP），以下情况可能发生：
>
> - **不保证向后兼容**：接口路径、请求参数、响应字段可能调整
> - **字段可能变更**：新增、删除或重命名字段
> - **行为可能调整**：错误码、默认值、限制值可能变化
>
> **建议**：
> - 生产环境使用前请确认版本兼容性
> - 关注变更日志（后续版本提供）
> - 客户端实现做好容错处理（忽略未知字段）

---

## 3. REST API

### 3.1 插件接口

#### 获取插件列表

```
GET /api/plugins
```

**响应示例**：

```json
{
  "plugins": [
    {
      "id": "plugins.rss_news.RssNewsAdapter",
      "name": "rss_news",
      "version": "1.0.0",
      "description": "RSS新闻采集",
      "author": "admin",
      "tags": ["news", "rss"],
      "enabled": true,
      "health_status": "unknown",
      "collection_mode": "full",
      "plugin_kind": "embedded",
      "execution_mode": "embedded_pipeline"
    },
    {
      "id": "plugins.dcp.DcpExternalCollectorAdapter",
      "name": "dcp",
      "version": "1.0.0",
      "description": "DCP外部采集器控制",
      "author": "admin",
      "tags": ["external", "dcp"],
      "enabled": true,
      "health_status": "unknown",
      "collection_mode": "full",
      "plugin_kind": "external",
      "execution_mode": "external_job"
    }
  ]
}
```

#### 获取插件配置

```
GET /api/plugins/{plugin_id}/config
```

**响应示例**：

```json
{
  "plugin_id": "plugins.rss_news.RssNewsAdapter",
  "config": {
    "feed_url": "https://example.com/feed.xml"
  }
}
```

#### 更新插件配置

```
PUT /api/plugins/{plugin_id}/config
```

**请求体**：

```json
{
  "feed_url": "https://new-example.com/feed.xml"
}
```

**响应示例**：

```json
{
  "success": true,
  "plugin_id": "plugins.rss_news.RssNewsAdapter",
  "config": {
    "feed_url": "https://new-example.com/feed.xml"
  }
}
```

#### 手动触发插件

```
POST /api/plugins/{plugin_id}/trigger
```

**请求体**：

```json
{
  "config": {
    "feed_url": "https://example.com/feed.xml"
  }
}
```

**响应示例**：

```json
{
  "success": true,
  "plugin_id": "plugins.rss_news.RssNewsAdapter",
  "collected": 50,
  "saved_ids": []
}
```

---

### 3.2 数据查询接口

#### 查询原始数据

```
GET /api/data
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plugin_id | string | 否 | 插件ID过滤 |
| limit | integer | 否 | 返回数量限制，默认20，最大100 |
| offset | integer | 否 | 偏移量，默认0 |

**响应示例**：

```json
{
  "total": 1000,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "plugin_id": "plugins.rss_news.RssNewsAdapter",
      "source": "rss",
      "data": {"title": "xxx", "link": "https://..."},
      "created_at": "2026-03-22T10:30:00"
    }
  ]
}
```

#### 查询规范化数据

```
GET /api/data/normalized
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plugin_id | string | 否 | 插件ID过滤 |
| event_type | string | 否 | 事件类型过滤（如 news/social/finance/alert） |
| limit | integer | 否 | 返回数量限制，默认20，最大100 |
| offset | integer | 否 | 偏移量，默认0 |

**响应示例**：

```json
{
  "total": 1000,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "plugin_id": "plugins.rss_news.RssNewsAdapter",
      "event_type": "news",
      "event_source": "RSS",
      "entity": ["xxx"],
      "event_timestamp": "2026-03-22T10:30:00",
      "unique_key": "abc123",
      "payload": {"title": "xxx"},
      "confidence": 1.0,
      "created_at": "2026-03-22T10:30:00"
    }
  ]
}
```

---

### 3.3 系统状态接口

#### 获取系统统计信息

```
GET /api/stats
```

**响应示例**：

```json
{
  "plugins": 3,
  "raw_data": 1500,
  "normalized_data": 1200,
  "task_stats": [
    {
      "plugin_id": "plugins.rss_news.RssNewsAdapter",
      "run_count": 10,
      "fail_count": 0,
      "last_run": "2026-03-22T10:30:00",
      "consecutive_fails": 0
    }
  ]
}
```

---

## 4. Ingestion API（上游数据接入）

### 4.1 批量接入 SourceEvent

```
POST /ingestion/v1/events
```

**请求体**：

```json
{
  "source_system": "dcp",
  "events": [
    {
      "event_id": "evt_001",
      "idempotency_key": "idmp_001",
      "source_record_key": "rec_001",
      "raw_event_key": "raw_001",
      "source_event_type": "daily_meeting",
      "event_granularity": "record",
      "dataset_key": "dcp.daily_meeting",
      "collection": "meetings",
      "page_name": "daily_report",
      "api_name": "get_meetings",
      "source_file": "meetings.json",
      "occurred_at": "2026-05-01T10:00:00",
      "collected_at": "2026-05-01T10:05:00",
      "payload": {"title": "每日例会", "participants": ["张三", "李四"]},
      "source_ref": "dcp://meetings/001",
      "event": "{"type": "meeting"}"
    }
  ]
}
```

**响应示例**：

```json
{
  "success": true,
  "received": 1,
  "saved": 1,
  "duplicates": 0,
  "errors": []
}
```

**SourceEvent 字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event_id | string | 是 | 事件唯一标识 |
| idempotency_key | string | 是 | 幂等键，防止重复接入 |
| source_record_key | string | 是 | 上游记录键 |
| raw_event_key | string | 是 | 原始事件键 |
| source_system | string | 是 | 上游系统名称 |
| source_event_type | string | 是 | 上游事件类型 |
| event_granularity | string | 是 | 事件粒度 |
| dataset_key | string | 否 | 数据集标识，用于路由 normalizer |
| payload | object | 是 | 原始数据载荷 |
| occurred_at | string | 否 | 事件发生时间（ISO 8601） |
| collected_at | string | 是 | 数据采集时间（ISO 8601） |

---

## 5. Processing API（归一化处理）

### 5.1 前台运行归一化

```
POST /processing/v1/run
```

**请求体**：

```json
{
  "dataset_key": "dcp.daily_meeting",
  "mode": "incremental",
  "batch_size": 1000
}
```

**响应示例**：

```json
{
  "success": true,
  "dataset_key": "dcp.daily_meeting",
  "processed": 150,
  "mode": "incremental",
  "duration_ms": 1234
}
```

### 5.2 提交后台归一化作业

```
POST /processing/v1/jobs
```

**请求体**：

```json
{
  "dataset_key": "dcp.daily_meeting",
  "mode": "incremental",
  "batch_size": 1000
}
```

**响应示例**：

```json
{
  "success": true,
  "job_id": "job_abc123",
  "status": "pending"
}
```

### 5.3 查询作业状态

```
GET /processing/v1/jobs/{job_id}
```

**响应示例**：

```json
{
  "job_id": "job_abc123",
  "dataset_key": "dcp.daily_meeting",
  "status": "completed",
  "mode": "incremental",
  "batch_size": 1000,
  "created_at": "2026-05-01T10:00:00",
  "started_at": "2026-05-01T10:00:01",
  "finished_at": "2026-05-01T10:00:05",
  "result": {"processed": 150, "inserted": 100, "updated": 50},
  "error": null
}
```

### 5.4 运行 Monitor 数据集归一化

```
POST /processing/v1/run-monitor
```

**请求体**：

```json
{
  "dataset_key": "dcp.monitor",
  "mode": "incremental"
}
```

**响应示例**：

```json
{
  "success": true,
  "dataset_key": "dcp.monitor",
  "processed": 500
}
```

---

## 6. Sandbox API（下游应用接口）

> **定位**：为特定下游应用（如数字沙盘）提供专用数据查询接口。
> 
> **核心原则**：
> - 数据隔离：返回标准化 DTO，不暴露原始 DCP 字段
> - 专用语义：接口命名和数据结构贴合下游应用需求

### 6.1 获取可用日期列表

```
GET /api/v1/sandbox/dates
```

**响应示例**：

```json
{
  "dates": ["2026-05-01", "2026-05-02", "2026-05-03"]
}
```

### 6.2 获取地图骨架数据

```
GET /api/v1/sandbox/map/skeleton
```

**响应示例**：

```json
{
  "stations": [
    {
      "id": "station_001",
      "name": "站点A",
      "lat": 39.9042,
      "lng": 116.4074
    }
  ],
  "towers": [
    {
      "id": "tower_001",
      "name": "杆塔A",
      "station_id": "station_001",
      "lat": 39.9045,
      "lng": 116.4078
    }
  ]
}
```

### 6.3 获取地图汇总数据

```
GET /api/v1/sandbox/map/summary
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期过滤（YYYY-MM-DD） |

**响应示例**：

```json
{
  "date": "2026-05-01",
  "station_count": 10,
  "tower_count": 50,
  "alert_count": 3,
  "summary": {
    "normal": 45,
    "warning": 3,
    "critical": 2
  }
}
```

---

## 7. RSS Feed

### 7.1 RSS订阅

```
GET /feed/rss
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tag | string | 否 | 按标签筛选 |
| limit | integer | 否 | 返回条目数，默认50，最大200 |

**响应格式**：XML (application/rss+xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Data Collector Hub Feed</title>
    <link>http://localhost:8000</link>
    <description>Real-time data collection feed</description>
    <item>
      <title>RSS新闻 - xxx</title>
      <link>http://localhost:8000/api/data/normalized?id=1</link>
      <pubDate>Sun, 22 Mar 2026 10:30:00 GMT</pubDate>
      <description>...</description>
      <guid isPermaLink="false">abc123</guid>
    </item>
  </channel>
</rss>
```

---

## 8. WebSocket

### 8.1 准实时流推送

```
WebSocket: /ws/stream
```

**单轮询广播架构**：
- 连接后客户端发送 `set_filters` 配置过滤条件
- 服务端定时轮询并广播新数据

**客户端消息**（设置过滤）：

```json
{
  "action": "set_filters",
  "filters": {
    "plugins": ["rss_news"],
    "interval": 5
  }
}
```

**服务端消息**（数据推送）：

```json
{
  "type": "data",
  "timestamp": "2026-03-22T10:30:00",
  "count": 1,
  "items": [
    {
      "id": 1,
      "plugin_id": "rss_news",
      "event_type": "news",
      "payload": {"title": "xxx"}
    }
  ]
}
```

### 8.2 获取 WebSocket 统计

```
GET /ws/stats
```

**响应示例**：

```json
{
  "active_connections": 2,
  "clients": {
    "abc12345": {"plugins": ["rss_news"], "interval": 5}
  },
  "polling_task_count": 1
}
```

---

## 9. MCP Server 接口

> 📄 **协议标准**：[Model Context Protocol](https://modelcontextprotocol.io/)

MCP Server 提供 LLM 工具调用能力，使下游 LLM 应用（如 Claude Desktop、Cursor 等）可以直接调用数据采集功能。本项目提供的是对 MCP 能力的 HTTP 封装映射。

### 9.1 服务发现

**Endpoint**: `GET /mcp`

返回 MCP Server 元信息和可用工具列表。

**响应示例**:

```json
{
  "version": "1.0.0",
  "description": "Data Collector Hub MCP Tool Interface",
  "tools": [
    {
      "name": "list_plugins",
      "description": "List all registered data collection plugins with optional filtering",
      "parameters": { ... }
    },
    {
      "name": "query_data",
      "description": "Query collected data (raw or normalized) with filtering and pagination",
      "parameters": { ... }
    },
    {
      "name": "trigger_plugin",
      "description": "Manually trigger a plugin to collect data immediately",
      "parameters": { ... }
    }
  ]
}
```

### 9.2 工具调用

**Endpoint**: `POST /mcp/call`

LLM 通过此端点调用工具。

**请求体**:

```json
{
  "tool": "query_data",
  "parameters": {
    "event_type": "news",
    "limit": 5
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "tool": "query_data",
  "result": {
    "success": true,
    "data_type": "normalized",
    "total": 1,
    "limit": 5,
    "offset": 0,
    "data": [
      {
        "id": 1,
        "plugin_id": "plugins.rss_news.RssNewsAdapter",
        "event_type": "news",
        "event_source": "RSS",
        "event_timestamp": "2026-03-22T10:30:00"
      }
    ]
  }
}
```

---

## 10. 错误码

HTTP状态码通常对应以下情况：

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 / MCP工具不存在 |
| 404 | 插件不存在 |
| 500 | 服务器内部错误 / 插件执行异常 |

**错误响应示例**：

```json
{
  "detail": "Plugin not found: xxx"
}
```

---

## 11. 接口变更记录

| 版本 | 变更内容 | 日期 |
|------|----------|------|
| 1.0.0 | 基于代码实现更新API接口定义 | 2026-05-03 |
| 1.1.0 | 新增 Ingestion API、Processing API、Sandbox API | 2026-05-06 |

---

*文档版本: v1.1*
*最后更新: 2026-05-06*
