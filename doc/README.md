# Data Collector Hub - 文档中心

> 插件化数据枢纽 —— 统一接入多源数据，为下游应用提供标准化数据服务

---

## 文档列表

| 文档 | 说明 | 版本 |
|------|------|------|
| [01-overview.md](01-overview.md) | 项目总览、愿景与定位 | v1.1 |
| [02-prd.md](02-prd.md) | 产品需求文档（PRD） | v1.1 |
| [03-architecture.md](03-architecture.md) | 系统架构设计 | v1.1 |
| [04-data-model.md](04-data-model.md) | 数据模型设计 | v1.1 |
| [05-api-spec.md](05-api-spec.md) | API 接口规范 | v1.1 |
| [06-plugin-dev-guide.md](06-plugin-dev-guide.md) | 插件开发指南 | v1.1 |
| [07-operations.md](07-operations.md) | 运维手册 | v1.1 |

---

## 快速导航

### 按角色

| 角色 | 推荐阅读 |
|------|----------|
| **项目经理/产品经理** | [01-overview.md](01-overview.md) → [02-prd.md](02-prd.md) |
| **架构师** | [01-overview.md](01-overview.md) → [03-architecture.md](03-architecture.md) → [04-data-model.md](04-data-model.md) |
| **后端开发** | [03-architecture.md](03-architecture.md) → [04-data-model.md](04-data-model.md) → [05-api-spec.md](05-api-spec.md) |
| **插件开发** | [06-plugin-dev-guide.md](06-plugin-dev-guide.md) → [05-api-spec.md](05-api-spec.md) |
| **运维工程师** | [07-operations.md](07-operations.md) → [05-api-spec.md](05-api-spec.md) |
| **上游系统对接** | [05-api-spec.md](05-api-spec.md#4-ingestion-api上游数据接入) → [04-data-model.md](04-data-model.md#25-上游事件表-raw_events) |
| **下游应用开发** | [05-api-spec.md](05-api-spec.md#6-sandbox-api下游应用接口) → [04-data-model.md](04-data-model.md#27-实体数据表-canonical_entities) |

### 按主题

| 主题 | 相关文档 |
|------|----------|
| **项目定位与愿景** | [01-overview.md](01-overview.md) |
| **系统架构** | [03-architecture.md](03-architecture.md) |
| **数据存储** | [04-data-model.md](04-data-model.md) |
| **API 接口** | [05-api-spec.md](05-api-spec.md) |
| **插件开发** | [06-plugin-dev-guide.md](06-plugin-dev-guide.md) |
| **部署运维** | [07-operations.md](07-operations.md) |
| **上游数据接入** | [05-api-spec.md](05-api-spec.md#4-ingestion-api上游数据接入) |
| **下游数据消费** | [05-api-spec.md](05-api-spec.md#6-sandbox-api下游应用接口) |

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-03 | 初始版本 |
| v1.1 | 2026-05-06 | 更新项目定位为"插件化数据枢纽"；新增 Ingestion API、Processing API、Sandbox API 文档；更新数据模型（raw_events、canonical_entities、normalizer_state、processing_jobs）；更新架构图 |

---

## 核心概念速查

### 项目定位

**Data Collector Hub** 是一个**插件化数据枢纽**：
- **DCP 只是其中一个上游采集平台**，通过 SourceEvent 标准化接入
- **数字沙盘只是其中一个下游应用**，通过 Sandbox API 消费数据
- 系统保持开放，支持任意上游数据源和下游消费方

### 数据流

```
上游系统（如 DCP）        插件采集                下游应用（如数字沙盘）
     │                      │                          │
     │ POST /ingestion      │ fetch()                  │ GET /api/v1/sandbox
     ▼                      ▼                          ▼
┌──────────┐          ┌──────────┐              ┌──────────────┐
│raw_events│          │ raw_data │              │canonical_    │
│          │          │          │              │  entities    │
└────┬─────┘          └────┬─────┘              └──────────────┘
     │                     │
     │ Normalizer          │ normalize()
     ▼                     ▼
┌─────────────────┐  ┌──────────────┐
│canonical_entities│  │normalized_data│
└─────────────────┘  └──────────────┘
```

### 关键术语

| 术语 | 说明 |
|------|------|
| **SourceEvent** | 上游系统推送的标准化事件格式 |
| **Ingestion API** | 上游数据接入接口 |
| **Normalizer** | 将 raw_events 归一化为 canonical_entities 的处理器 |
| **Processing API** | 归一化处理接口 |
| **Sandbox API** | 下游应用专用数据接口 |
| **Plugin** | 数据采集插件，支持嵌入式和外部采集器控制两种模式 |

---

*文档版本: v1.1*
*最后更新: 2026-05-06*
