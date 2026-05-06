# Data Collector Hub - 插件开发指南

---

## 1. 插件架构概述

### 1.1 插件定位

Data Collector Hub 是一个**插件化数据枢纽**，插件是数据采集的核心扩展单元。系统支持两种数据采集模式：

1. **插件自主采集**：插件通过 `fetch()` 方法主动从数据源采集数据
2. **上游系统推送**：外部系统通过 Ingestion API 推送 SourceEvent，无需开发插件

### 1.2 插件类型

| 类型 | `plugin_kind` | `collection_mode` | 说明 |
|------|---------------|-------------------|------|
| **嵌入式插件** | `embedded` | `full` / `incremental` | 插件内部实现采集逻辑，直接获取数据 |
| **外部采集器控制** | `external` | `full` | 插件控制外部采集器（如 DCP），不直接获取数据 |

### 1.3 插件执行模式

| 模式 | `execution_mode` | 说明 |
|------|------------------|------|
| **嵌入式管道** | `embedded_pipeline` | 插件在系统内部执行采集管道 |
| **外部作业** | `external_job` | 插件触发外部作业，不直接处理数据 |

---

## 2. 快速开始

### 2.1 最小插件示例

```python
# plugins/my_plugin.py
from typing import List, Dict, Any
from core.base_adapter import BaseAdapter, DataItem

class MyPluginAdapter(BaseAdapter):
    """我的第一个插件"""

    # 插件元数据
    name = "my_plugin"
    version = "1.0.0"
    description = "示例插件"
    author = "your_name"
    tags = ["demo"]
    collection_mode = "full"  # "full" | "incremental"
    plugin_kind = "embedded"  # "embedded" | "external"
    execution_mode = "embedded_pipeline"

    async def fetch(self, **kwargs) -> List[DataItem]:
        """采集数据（必须实现）"""
        # 从数据源获取数据
        data = await self._fetch_from_source()

        # 转换为 DataItem 列表
        items = []
        for item in data:
            items.append(DataItem(
                source="my_source",
                data=item,
                timestamp=datetime.now()
            ))

        return items

    async def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """规范化数据（可选实现）"""
        normalized = []
        for item in raw_data:
            normalized.append({
                "event_type": "news",
                "event_source": item.get("source", "unknown"),
                "entity": [item.get("author", "")],
                "event_timestamp": item.get("published_at"),
                "title": item.get("title", ""),
                "payload": {
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "url": item.get("url")
                }
            })
        return normalized

    async def _fetch_from_source(self):
        """从数据源获取原始数据（私有方法）"""
        # 实现你的采集逻辑
        pass
```

### 2.2 插件注册

将插件文件放入 `plugins/` 目录，系统启动时自动发现和注册：

```
plugins/
├── __init__.py
├── my_plugin.py          # 你的插件
└── ...
```

---

## 3. BaseAdapter 接口详解

### 3.1 核心方法

```python
class BaseAdapter(ABC):
    """插件基类"""

    # 必须实现的属性
    name: str                    # 插件名称（唯一标识）
    version: str                 # 版本号
    description: str             # 描述
    author: str                  # 作者
    tags: List[str]              # 标签列表
    collection_mode: str         # "full" | "incremental"
    plugin_kind: str             # "embedded" | "external"
    execution_mode: str          # "embedded_pipeline" | "external_job"

    # 必须实现的方法
    @abstractmethod
    async def fetch(self, **kwargs) -> List[DataItem]:
        """采集数据，返回 DataItem 列表"""
        pass

    # 可选实现的方法
    async def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """规范化数据，返回标准化字典列表"""
        pass

    async def health_check(self) -> bool:
        """健康检查，返回是否健康"""
        return True
```

### 3.2 DataItem 数据模型

```python
@dataclass
class DataItem:
    source: str                  # 数据来源标识
    data: Dict[str, Any]         # 原始数据（JSON可序列化）
    timestamp: datetime          # 数据时间戳
    metadata: Dict[str, Any] = None  # 可选元数据
```

### 3.3 规范化数据格式

```python
# normalize() 方法返回的数据结构
{
    "event_type": "news",           # 事件类型：news/social/finance/alert
    "event_source": "RSS",          # 事件来源
    "entity": ["公司A", "人物B"],    # 实体列表（JSON数组）
    "event_timestamp": "2026-03-22T10:30:00",  # 事件时间
    "title": "新闻标题",             # 内容标识（用于去重）
    "payload": {                    # 标准化容器（保留原始状态）
        "title": "完整标题",
        "content": "内容...",
        "url": "https://..."
    }
}
```

---

## 4. 增量采集实现

### 4.1 时间戳型增量

适用于按时间递增的数据源（如新闻、日志）。

```python
class TimestampIncrementalAdapter(BaseAdapter):
    name = "timestamp_demo"
    collection_mode = "incremental"
    plugin_kind = "embedded"

    async def fetch(self, **kwargs) -> List[DataItem]:
        # 获取上次采集时间
        state = store.get_plugin_state(self.name)
        last_timestamp = state.get("last_timestamp") if state else None

        # 只采集新数据
        if last_timestamp:
            data = await self.fetch_since(last_timestamp)
        else:
            data = await self.fetch_all()

        # 保存新状态
        if data:
            store.save_plugin_state(
                self.name,
                last_timestamp=data[-1]["timestamp"]
            )

        return [DataItem(source="demo", data=d, timestamp=datetime.now()) for d in data]
```

### 4.2 游标型增量

适用于有ID或页码的数据源（如分页API）。

```python
class CursorIncrementalAdapter(BaseAdapter):
    name = "cursor_demo"
    collection_mode = "incremental"
    plugin_kind = "embedded"

    async def fetch(self, **kwargs) -> List[DataItem]:
        # 获取上次游标
        state = store.get_plugin_state(self.name)
        last_cursor = state.get("last_cursor") if state else None

        # 从上次位置继续采集
        data = await self.fetch_from_cursor(last_cursor)

        # 保存新游标
        if data:
            new_cursor = data[-1]["id"]
            store.save_plugin_state(
                self.name,
                last_cursor=new_cursor
            )

        return [DataItem(source="demo", data=d, timestamp=datetime.now()) for d in data]
```

### 4.3 偏移型增量

适用于固定分页的数据源。

```python
class OffsetIncrementalAdapter(BaseAdapter):
    name = "offset_demo"
    collection_mode = "incremental"
    plugin_kind = "embedded"

    async def fetch(self, **kwargs) -> List[DataItem]:
        # 获取上次偏移量
        state = store.get_plugin_state(self.name)
        last_offset = state.get("last_offset", 0) if state else 0

        # 从上次偏移量继续
        data = await self.fetch_page(offset=last_offset, limit=100)

        # 保存新偏移量
        if data:
            store.save_plugin_state(
                self.name,
                last_offset=last_offset + len(data)
            )

        return [DataItem(source="demo", data=d, timestamp=datetime.now()) for d in data]
```

### 4.4 自定义状态

适用于复杂状态需求。

```python
class CustomStateAdapter(BaseAdapter):
    name = "custom_demo"
    collection_mode = "incremental"
    plugin_kind = "embedded"

    async def fetch(self, **kwargs) -> List[DataItem]:
        # 获取自定义状态
        state = store.get_plugin_state(self.name)
        custom_state = state.get("state_data", {}) if state else {}

        last_page = custom_state.get("last_page", 1)
        processed_ids = custom_state.get("processed_ids", [])

        # 采集逻辑...

        # 保存自定义状态
        store.save_plugin_state(
            self.name,
            state_data={
                "last_page": last_page + 1,
                "processed_ids": processed_ids + new_ids
            }
        )

        return items
```

---

## 5. 外部采集器控制插件

### 5.1 场景说明

当数据源需要通过外部系统（如 DCP 平台）采集时，插件不直接获取数据，而是：
1. 触发外部采集器启动
2. 监控采集器状态
3. 外部系统通过 Ingestion API 推送数据

### 5.2 外部采集器控制示例

```python
class ExternalCollectorAdapter(BaseAdapter):
    """外部采集器控制插件示例"""

    name = "external_collector"
    version = "1.0.0"
    description = "控制外部采集器"
    author = "admin"
    tags = ["external"]
    collection_mode = "full"
    plugin_kind = "external"          # 外部采集器
    execution_mode = "external_job"   # 外部作业模式

    async def fetch(self, **kwargs) -> List[DataItem]:
        """
        触发外部采集器

        注意：外部采集器插件通常不直接返回数据，
        而是触发外部系统采集，数据通过 Ingestion API 接入
        """
        # 触发外部采集器
        await self.trigger_external_collector()

        # 返回空列表（数据由外部系统推送）
        return []

    async def trigger_external_collector(self):
        """触发外部采集器启动"""
        # 调用外部系统 API 启动采集
        pass

    async def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        外部采集器插件通常不需要实现 normalize
        因为数据通过 Ingestion API 接入后由 Normalizer 处理
        """
        return []
```

### 5.3 DCP 外部采集器控制（实际示例）

```python
# plugins/dcp.py
class DcpExternalCollectorAdapter(BaseAdapter):
    """DCP外部采集器控制插件"""

    name = "dcp"
    version = "1.0.0"
    description = "DCP外部采集器控制"
    author = "admin"
    tags = ["external", "dcp"]
    collection_mode = "full"
    plugin_kind = "external"
    execution_mode = "external_job"

    async def fetch(self, **kwargs) -> List[DataItem]:
        """触发 DCP 采集器"""
        # 1. 检查 DCP 采集器状态
        # 2. 发送采集指令
        # 3. 数据由 DCP 通过 Ingestion API 推送
        return []
```

---

## 6. 完整插件示例

### 6.1 RSS新闻采集插件

```python
# plugins/rss_news.py
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from core.base_adapter import BaseAdapter, DataItem

class RssNewsAdapter(BaseAdapter):
    """RSS新闻采集插件"""

    name = "rss_news"
    version = "1.0.0"
    description = "RSS新闻采集"
    author = "admin"
    tags = ["news", "rss"]
    collection_mode = "incremental"
    plugin_kind = "embedded"
    execution_mode = "embedded_pipeline"

    async def fetch(self, **kwargs) -> List[DataItem]:
        """采集RSS数据"""
        config = kwargs.get("config", {})
        feed_url = config.get("feed_url", "https://example.com/feed.xml")

        # 获取上次采集时间
        state = store.get_plugin_state(self.name)
        last_timestamp = state.get("last_timestamp") if state else None

        # 解析RSS
        feed = feedparser.parse(feed_url)

        items = []
        for entry in feed.entries:
            published = datetime.strptime(
                entry.published,
                "%a, %d %b %Y %H:%M:%S %z"
            )

            # 增量过滤
            if last_timestamp and published <= last_timestamp:
                continue

            items.append(DataItem(
                source="rss",
                data={
                    "title": entry.title,
                    "link": entry.link,
                    "published": published.isoformat(),
                    "summary": entry.get("summary", "")
                },
                timestamp=published
            ))

        # 保存状态
        if items:
            store.save_plugin_state(
                self.name,
                last_timestamp=max(item.timestamp for item in items)
            )

        return items

    async def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """规范化RSS数据"""
        normalized = []
        for item in raw_data:
            normalized.append({
                "event_type": "news",
                "event_source": "RSS",
                "entity": [],
                "event_timestamp": item.get("published"),
                "title": item.get("title", ""),
                "payload": {
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "summary": item.get("summary")
                }
            })
        return normalized
```

### 6.2 上游系统接入（无需插件）

对于上游系统（如 DCP）推送数据，**无需开发插件**，直接调用 Ingestion API：

```python
# 上游系统（如 DCP）调用示例
import requests

events = [
    {
        "event_id": "evt_001",
        "idempotency_key": "idmp_001",
        "source_record_key": "rec_001",
        "raw_event_key": "raw_001",
        "source_event_type": "daily_meeting",
        "event_granularity": "record",
        "dataset_key": "dcp.daily_meeting",
        "payload": {"title": "每日例会", "participants": ["张三", "李四"]},
        "source_ref": "dcp://meetings/001",
        "event": "{\"type\": \"meeting\"}",
        "collected_at": "2026-05-01T10:05:00"
    }
]

response = requests.post(
    "http://localhost:8000/ingestion/v1/events",
    json={
        "source_system": "dcp",
        "events": events
    }
)
```

---

## 7. 插件开发规范

### 7.1 命名规范

| 项目 | 规范 | 示例 |
|------|------|------|
| 插件文件名 | 小写下划线 | `rss_news.py` |
| 类名 | PascalCase + Adapter | `RssNewsAdapter` |
| 插件名称 | 小写下划线 | `rss_news` |
| 版本号 | 语义化版本 | `1.0.0` |

### 7.2 错误处理

```python
async def fetch(self, **kwargs) -> List[DataItem]:
    try:
        # 采集逻辑
        data = await self._fetch_data()
        return data
    except requests.RequestException as e:
        # 网络错误
        logger.error(f"Network error: {e}")
        raise
    except Exception as e:
        # 其他错误
        logger.error(f"Unexpected error: {e}")
        raise
```

### 7.3 日志记录

```python
import logging

logger = logging.getLogger(__name__)

async def fetch(self, **kwargs) -> List[DataItem]:
    logger.info(f"Starting fetch for {self.name}")

    # 采集逻辑
    items = await self._fetch_data()

    logger.info(f"Fetched {len(items)} items")
    return items
```

### 7.4 配置管理

```python
async def fetch(self, **kwargs) -> List[DataItem]:
    # 从 kwargs 获取运行时配置
    config = kwargs.get("config", {})

    # 从数据库获取持久化配置
    db_config = store.get_plugin_config(self.name)

    # 合并配置（运行时配置优先）
    merged_config = {**db_config, **config}

    # 使用配置
    feed_url = merged_config.get("feed_url")
    timeout = merged_config.get("timeout", 30)

    # ...
```

---

## 8. 插件调试

### 8.1 本地测试

```python
# test_my_plugin.py
import asyncio
from plugins.my_plugin import MyPluginAdapter

async def test():
    adapter = MyPluginAdapter()

    # 测试 fetch
    items = await adapter.fetch()
    print(f"Fetched {len(items)} items")

    # 测试 normalize
    if items:
        raw_data = [item.data for item in items]
        normalized = await adapter.normalize(raw_data)
        print(f"Normalized {len(normalized)} items")

if __name__ == "__main__":
    asyncio.run(test())
```

### 8.2 手动触发

通过 REST API 手动触发插件：

```bash
curl -X POST http://localhost:8000/api/plugins/my_plugin/trigger \
  -H "Content-Type: application/json" \
  -d '{"config": {"key": "value"}}'
```

---

## 9. 插件生命周期

```
┌─────────────┐
│   开发      │
│  编写代码   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   注册      │
│ 放入plugins/ │
│  自动发现   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   配置      │
│  设置参数   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   调度      │
│  Scheduler  │
│  定时触发   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   执行      │
│  fetch()    │
│  normalize()│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   存储      │
│  raw_data   │
│ normalized_ │
│    data     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   查询      │
│  REST API   │
│  RSS Feed   │
│  WebSocket  │
└─────────────┘
```

---

## 10. 常见问题

### Q1: 插件和上游系统接入有什么区别？

**A**: 
- **插件**：系统主动去数据源采集，适用于系统可控的数据源
- **上游系统接入**：外部系统主动推送数据，适用于外部系统主导的数据源

### Q2: 外部采集器控制插件为什么不返回数据？

**A**: 外部采集器控制插件的职责是触发外部系统采集，数据由外部系统通过 Ingestion API 推送，因此 `fetch()` 通常返回空列表。

### Q3: 如何实现插件间的数据依赖？

**A**: MVP 阶段**不允许**插件间依赖。每个插件必须独立运行。如果需要在插件B中使用插件A的数据，应该通过数据库查询或 REST API 获取。

### Q4: 插件配置如何持久化？

**A**: 插件配置存储在 `plugins` 表的 `config` 字段（JSON格式）和 `plugin_runtime_configs` 表中。通过 REST API 更新配置时会持久化到数据库。

### Q5: 如何监控插件运行状态？

**A**: 
1. 查看 `task_stats` 表获取运行统计
2. 调用 `/api/stats` 获取系统状态
3. 查看 `logs` 表获取详细日志
4. 使用 `health_check()` 方法实现自定义健康检查

---

*文档版本: v1.1*
*最后更新: 2026-05-06*
