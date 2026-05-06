# Data Collector Hub v1.1

> 插件化数据枢纽 —— 统一接入多源数据，为下游应用提供标准化数据服务

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)](https://sqlite.org)
[![uv](https://img.shields.io/badge/uv-astral-purple.svg)](https://docs.astral.sh/uv/)
[![Version](https://img.shields.io/badge/Version-1.1-success.svg)]()

---

## 产品定位

**Data Collector Hub** 是一个**插件化数据枢纽**，定位于数据底座，为各类下游应用提供统一的数据接入、存储与服务能力。

```
┌─────────────────────────────────────────────────────────────────┐
│                    上游数据采集层                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ DCP平台 │ │ RSS新闻 │ │ 社交媒体│ │ 财经数据│ │ 其他API │   │
│  │ (外部)  │ │ (内置)  │ │ (插件)  │ │ (插件)  │ │ (插件)  │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│       └─────────────┴─────────────┴─────────────┴─────────────┘   │
│                           │                                      │
│                           ▼                                      │
│              ┌─────────────────────────────┐                     │
│              │   Data Collector Hub        │                     │
│              │   ┌─────────────────────┐   │                     │
│              │   │  Ingestion API      │   │  ← SourceEvent接入  │
│              │   │  Plugin Pipeline    │   │  ← 插件采集管道     │
│              │   │  Normalizer Runner  │   │  ← 归一化处理       │
│              │   │  Canonical Store    │   │  ← 实体存储         │
│              │   └─────────────────────┘   │                     │
│              │   SQLite + REST API         │                     │
│              │   RSS + WebSocket + MCP     │                     │
│              └──────────┬──────────────────┘                     │
└─────────────────────────┼───────────────────────────────────────┘
                          │ 局域网/本地服务
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    下游应用层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 数字沙盘     │  │ LLM舆情推演   │  │ 分析报告生成  │          │
│  │ 实时态势展示 │  │ 热点/情绪/风险│  │ 宏观/中观/微观│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 数据大屏     │  │ AI Agent     │  │ 其他消费方   │          │
│  │ 可视化展示   │  │ 自动化工作流  │  │ (API/RSS/WS) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

**核心设计原则**：
- **DCP 只是其中一个上游采集平台**，通过 SourceEvent 标准化接入
- **数字沙盘只是其中一个下游应用**，通过 Sandbox API 消费数据
- 系统保持开放，支持任意上游数据源和下游消费方

---

## 核心特性

### 插件化架构
- **懒加载发现**：基于 AST 解析，无需导入即可提取插件元数据
- **扁平化设计**：一个数据源 = 一个独立文件，逻辑隔离
- **延迟实例化**：用时才 import，降低启动开销
- **多模式支持**：嵌入式采集管道 + 外部采集器控制（如 DCP）

### 多协议数据服务
- **REST API**：结构化数据查询（FastAPI）
- **RSS Feed**：订阅推送（RSS 2.0）
- **WebSocket**：准实时流推送（单轮询广播模式）
- **MCP**：LLM 工具调用接口（Model Context Protocol）
- **Sandbox API**：下游应用专用数据接口（如数字沙盘）

### 数据管道
- **多层数据架构**：
  - `raw_data`：插件采集的原始数据
  - `raw_events`：上游系统推送的标准化 SourceEvent
  - `normalized_data`：轻量级规范化数据
  - `canonical_entities`：下游应用消费的实体数据
- **自动去重**：基于 MD5 unique_key 的重复检测
- **增量采集**：支持状态保存的增量模式
- **归一化处理**：可配置的 normalizer 将 raw_events 转换为 canonical_entities

### 任务调度
- **APScheduler**：可靠的定时任务调度
- **并发控制**：Semaphore 控制协程级并发
- **超时保护**：asyncio.wait_for 防止任务挂起
- **失败隔离**：单插件失败不影响其他任务

### Web 管理界面
- **Streamlit 管理界面**：数据面板 + 运行时配置管理
- **实时数据查看**：插件状态、原始数据、规范化数据、实体数据
- **任务统计**：采集统计、日志查看、处理作业状态

---

## 快速开始

### 环境要求

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) - Python 包管理器

### 安装 uv（如果尚未安装）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 克隆并安装

```bash
# 克隆仓库
git clone <repository-url>
cd vibe-DataCollectorHub

# 使用 uv 创建虚拟环境并安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 启动服务

```bash
# 同时启动 API 服务和 Streamlit 管理界面
uv run run.py
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 根端点：http://localhost:8000/
- 管理界面：http://localhost:8501

### 运行测试

```bash
# 运行 pytest 自动化测试
uv run pytest

# 运行集成测试脚本
uv run python tests/scripts/test_integration_rc1.py
uv run python tests/scripts/test_api.py
uv run python tests/scripts/test_websocket_verification.py
```

---

## API 接口

### 插件管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/plugins` | GET | 获取插件列表 |
| `/api/plugins/{id}/trigger` | POST | 手动触发插件 |

### 数据查询

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/data` | GET | 查询 raw_data（插件采集原始数据） |
| `/api/data/normalized` | GET | 查询 normalized_data（规范化数据） |
| `/api/stats` | GET | 系统统计信息 |

### SourceEvent 接入

| 端点 | 方法 | 说明 |
|------|------|------|
| `/ingestion/v1/events` | POST | 批量接入上游 SourceEvent |

### 归一化处理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/processing/v1/run` | POST | 前台运行归一化（调试用） |
| `/processing/v1/jobs` | POST | 提交后台归一化作业 |
| `/processing/v1/jobs/{job_id}` | GET | 查询作业状态 |
| `/processing/v1/run-monitor` | POST | 运行 Monitor 数据集归一化 |

### Sandbox API（下游应用）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/sandbox/dates` | GET | 获取可用日期列表（时间轴模式） |
| `/api/v1/sandbox/map/skeleton` | GET | 获取地图骨架数据（站点/杆塔） |

### RSS Feed

| 端点 | 说明 |
|------|------|
| `/feed/rss` | RSS 2.0 订阅源 |

### WebSocket

| 端点 | 说明 |
|------|------|
| `/ws/stream` | 实时数据流 |
| `/ws/stats` | 连接统计 |

### MCP (Model Context Protocol)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/mcp` | GET | 工具发现 |
| `/mcp/call` | POST | 工具调用 |

**支持的 MCP 工具**：
- `list_plugins` - 列出插件
- `query_data` - 查询数据
- `trigger_plugin` - 触发插件

---

## 项目结构

```
DataCollectorHub/
├── api/                           # API 服务层
│   └── server.py                 # FastAPI 主服务
├── core/                          # 核心引擎层
│   ├── base_adapter.py           # 插件基类
│   ├── plugin_manager.py         # 插件管理（AST 懒加载）
│   ├── plugin_config_validator.py # 运行时配置校验
│   ├── dataset_resolver.py       # Dataset 解析（DCP 等）
│   ├── paths.py                  # 项目路径管理
│   ├── pipeline.py               # 数据管道
│   ├── scheduler.py              # 任务调度
│   ├── websocket_manager.py      # WebSocket 管理
│   └── mcp_tools.py              # MCP 工具
├── storage/                       # 存储层
│   └── sqlite_store.py           # SQLite 存储 + Schema 管理
├── processing/                    # 归一化处理层
│   ├── normalizer_runner.py      # Normalizer 运行器
│   └── dcp/                      # DCP 专用 normalizers
│       ├── daily_meeting.py
│       ├── station.py
│       └── tower.py
├── plugins/                       # 插件层
│   ├── _base/                    # 基础类目录
│   ├── demo_plugin.py            # 示例插件
│   ├── rss_news.py               # RSS 新闻插件
│   └── dcp.py                    # DCP 外部采集器控制插件
├── dashboard/                     # Web 管理界面 (Streamlit)
│   └── app.py                    # Streamlit 应用
├── doc/                           # 设计文档
│   ├── 01-overview.md
│   ├── 02-prd.md
│   ├── 03-architecture.md
│   ├── 04-data-model.md
│   ├── 05-api-spec.md
│   ├── 06-plugin-dev-guide.md
│   ├── 07-operations.md
│   └── decisions/                # ADR 架构决策记录
├── tests/                         # 测试与验证
│   ├── conftest.py               # pytest 共享配置
│   ├── test_*.py                 # 自动化测试
│   └── scripts/                  # 手动冒烟/集成验证脚本
├── pyproject.toml                 # uv 项目配置
├── uv.lock                        # 锁定依赖版本
├── run.py                         # 同时启动 API + Dashboard
└── run_scheduler.py               # 独立调度器模式
```

---

## 开发插件

### 最小插件示例（嵌入式采集）

```python
from core.base_adapter import BaseAdapter, DataItem
from typing import List, Optional
from datetime import datetime

class MyPlugin(BaseAdapter):
    name = "my_plugin"
    version = "1.0.0"
    description = "My data collector plugin"
    author = "developer"
    tags = ["demo"]
    config_schema = {}
    dependencies = []
    collection_mode = "full"

    async def fetch(self, **kwargs) -> List[DataItem]:
        return [
            DataItem(
                source="api",
                plugin_id=self.name,
                timestamp=datetime.now(),
                data={"title": "Example", "content": "..."},
                metadata={}
            )
        ]

    def normalize(self, raw_data: dict, raw_data_id: int) -> Optional[dict]:
        return {
            "event_type": "news",
            "event_source": "api",
            "entity": [],
            "event_timestamp": datetime.now(),
            "title": raw_data.get("title", ""),
            "payload": raw_data,
            "confidence": 1.0
        }
```

### 外部采集器控制插件示例

```python
from core.base_adapter import BaseAdapter, DataItem

class ExternalCollectorAdapter(BaseAdapter):
    """外部采集器控制插件 —— 不直接采集，管理外部系统配置"""

    name = "external_collector"
    version = "1.0.0"
    plugin_kind = "external"
    execution_mode = "external_job"

    async def fetch(self, **kwargs) -> List[DataItem]:
        # 外部系统负责实际采集，本插件仅做控制
        return []
```

将插件文件放入 `plugins/` 目录即可自动发现。

---

## 数据流

### 插件采集数据流

```
┌─────────────┐
│ plugin.fetch│
└──────┬──────┘
       ▼
┌─────────────┐
│  raw_data   │
└──────┬──────┘
       ▼
┌─────────────┐
│  normalize  │ (optional)
└──────┬──────┘
       ▼
┌─────────────┐
│ unique_key  │ (MD5 hash)
└──────┬──────┘
       ▼
┌─────────────┐
│normalized_data│
└─────────────┘
```

### SourceEvent 接入数据流（如 DCP）

```
┌─────────────────┐
│ 上游系统        │
│ (vibe-downloader)│
└────────┬────────┘
         │ POST /ingestion/v1/events
         ▼
┌─────────────────┐
│ SourceEvent     │
│ 校验 + 解析     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  raw_events     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Normalizer      │
│ (processing/dcp)│
└────────┬────────┘
         ▼
┌─────────────────┐
│canonical_entities│ ← 下游应用消费
└─────────────────┘
```

---

## Streamlit 管理界面

### 功能特性

- **插件状态**：查看所有插件的启用状态和健康状态
- **数据浏览**：查看原始数据、SourceEvent、规范化数据、实体数据
- **任务统计**：采集成功率、失败次数等统计信息
- **日志查看**：实时查看系统日志
- **运行时配置**：管理插件运行时配置（如 DCP 数据集开关）

### 启动方式

```bash
# 开发模式（自动重载）
uv run python -m streamlit run dashboard/app.py

# 生产模式
uv run streamlit run dashboard/app.py --server.port 8501
```

---

## 常用命令

```bash
# 安装依赖
uv sync

# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 同时运行 API 服务和管理界面
uv run run.py

# 单独运行 API 服务（调试）
uv run python -m uvicorn api.server:app --reload

# 单独运行管理界面（调试）
uv run python -m streamlit run dashboard/app.py

# 运行测试
uv run pytest

# 更新依赖
uv sync --upgrade
```

---

## 设计约束

v1.1 版本的设计约束（非缺陷）：

| 约束 | 说明 |
|------|------|
| 单节点部署 | 不支持分布式 |
| SQLite 唯一存储 | 不支持 PostgreSQL/MySQL |
| 无认证/权限 | 无用户管理系统 |
| 协程级隔离 | 非进程级沙箱 |
| 无插件依赖 | 插件间无法相互调用 |
| 日志仅本地 | 无远程日志收集 |

---

## 测试

### 运行所有测试

```bash
# 运行 pytest 自动化测试
uv run pytest

# 集成验收测试
uv run python tests/scripts/test_integration_rc1.py

# WebSocket 专项测试
uv run python tests/scripts/test_websocket_verification.py

# API 测试
uv run python tests/scripts/test_api.py
```

### 测试覆盖

- ✅ Plugin Discovery
- ✅ Pipeline (raw → normalized)
- ✅ Scheduler
- ✅ REST API
- ✅ RSS Feed
- ✅ WebSocket
- ✅ MCP
- ✅ SourceEvent Ingestion
- ✅ Normalizer Runner
- ✅ Streamlit 管理界面

---

## 文档

| 文档 | 内容 |
|------|------|
| [doc/01-overview.md](doc/01-overview.md) | 产品愿景、总体架构 |
| [doc/02-prd.md](doc/02-prd.md) | 产品需求、SLA |
| [doc/03-architecture.md](doc/03-architecture.md) | 架构设计 |
| [doc/04-data-model.md](doc/04-data-model.md) | 数据模型 |
| [doc/05-api-spec.md](doc/05-api-spec.md) | API 规范 |
| [doc/06-plugin-dev-guide.md](doc/06-plugin-dev-guide.md) | 插件开发指南 |
| [doc/07-operations.md](doc/07-operations.md) | 运维治理 |
| [V1_0_FEATURE_LIST.md](V1_0_FEATURE_LIST.md) | v1.0 功能清单（历史） |
| [V1_0_KNOWN_ISSUES.md](V1_0_KNOWN_ISSUES.md) | 已知问题（历史） |

---

## 版本信息

- **当前版本**: v1.1
- **发布日期**: 2026-05-06
- **状态**: Stable

---

## License

MIT License

---

*Data Collector Hub - 插件化数据枢纽*
