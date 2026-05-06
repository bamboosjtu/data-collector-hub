# ADR-007: DCP 作为上游采集平台集成

## 状态

- 状态: 已接受
- 日期: 2026-05-06

## 背景

DCP（Data Collection Platform）是公司内部的一个数据采集平台，需要将其采集的数据接入 Data Collector Hub。关键约束：

1. DCP 有自己的采集逻辑和调度机制，不希望通过插件直接控制其内部实现
2. DCP 采集的数据需要经过标准化后才能被下游应用消费
3. 系统定位是数据枢纽，DCP 只是其中一个上游来源

## 决策

**DCP 通过外部采集器控制插件 + Ingestion API 接入，不直接暴露 DCP 原始字段给下游。**

```
DCP 平台
    │
    │ 1. DCP 插件触发外部采集
    ▼
plugins/dcp.py (external plugin_kind)
    │
    │ 2. 外部采集器推送数据
    ▼
POST /ingestion/v1/events (SourceEvent)
    │
    │ 3. 标准化存储
    ▼
raw_events (保留原始 payload)
    │
    │ 4. Normalizer 处理
    ▼
canonical_entities (面向下游的标准化数据)
    │
    │ 5. 下游应用消费
    ▼
Sandbox API (返回 DTO，不暴露原始字段)
```

## 原因

### 1. 职责分离

| 组件 | 职责 |
|------|------|
| DCP 平台 | 数据采集、原始数据生成 |
| DCP 插件 | 触发/协调外部采集器 |
| Ingestion API | 标准化接入、幂等性保证 |
| Normalizer | 数据归一化、实体提取 |
| Sandbox API | 下游数据服务、DTO 转换 |

### 2. 避免紧耦合

- DCP 的原始数据格式变化不影响下游应用
- 下游应用通过 canonical_entities 消费数据，与 DCP 解耦
- Sandbox API 返回 DTO，完全隔离 DCP 原始字段

### 3. 支持多上游系统

同样的架构可以复用于其他上游系统：
- 每个上游系统通过 SourceEvent 标准化接入
- 通过 `source_system` 字段区分来源
- 通过 `dataset_key` 路由到对应的 Normalizer

## 影响

### 正面影响

- DCP 和 Data Collector Hub 解耦
- 下游应用不依赖 DCP 数据格式
- 支持未来接入其他类似平台

### 负面影响

- 增加一层数据转换（SourceEvent → canonical_entities）
- 需要维护 Normalizer 映射逻辑
- 实时性受限于推送频率

## 替代方案

### 方案 A：DCP 直接写入数据库（已拒绝）

DCP 直接写入 Data Collector Hub 的数据库。

**拒绝原因**：
- 破坏数据枢纽的边界，DCP 需要了解内部表结构
- 无法做标准化校验和幂等性控制
- 安全问题：直接数据库访问权限过大

### 方案 B：DCP 插件直接采集（已拒绝）

开发一个 embedded 插件，直接调用 DCP API 采集数据。

**拒绝原因**：
- DCP 的采集逻辑复杂，不适合在插件中重写
- DCP 有自己的调度机制，与系统调度器冲突
- 无法利用 DCP 的现有采集能力

## 相关决策

- ADR-005: 三层数据架构
- ADR-008: SourceEvent 标准化接入协议
- ADR-009: Sandbox API 下游应用接口

## 备注

- DCP 插件的 `plugin_kind` 为 `external`，`execution_mode` 为 `external_job`
- DCP 推送数据时必须提供 `idempotency_key` 保证幂等性
- `dataset_key` 格式建议：`dcp.<collection_name>`
