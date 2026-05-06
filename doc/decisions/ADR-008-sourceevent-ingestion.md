# ADR-008: SourceEvent 标准化接入协议

## 状态

- 状态: 已接受
- 日期: 2026-05-06

## 背景

Data Collector Hub 作为数据枢纽，需要接入多个上游系统的数据。不同上游系统的数据格式各异，需要一种标准化的接入协议来：

1. 统一数据接入格式，降低接入成本
2. 保证数据可追溯（数据来源、采集时间等）
3. 支持幂等性，防止重复数据
4. 保留原始数据用于问题排查

## 决策

**采用 SourceEvent 作为上游系统标准化接入协议，通过 Ingestion API (`POST /ingestion/v1/events`) 接收。**

### SourceEvent 核心字段

```json
{
  "event_id": "evt_001",              // 事件唯一标识
  "idempotency_key": "idmp_001",      // 幂等键（必需）
  "source_record_key": "rec_001",     // 上游记录键
  "raw_event_key": "raw_001",         // 原始事件键
  "source_system": "dcp",             // 上游系统名称
  "source_event_type": "daily_meeting", // 上游事件类型
  "event_granularity": "record",      // 事件粒度
  "dataset_key": "dcp.daily_meeting", // 数据集标识（路由 Normalizer）
  "payload": {...},                   // 原始数据载荷（JSON）
  "occurred_at": "2026-05-01T10:00:00", // 事件发生时间
  "collected_at": "2026-05-01T10:05:00", // 数据采集时间（必需）
  "source_ref": "dcp://meetings/001"  // 来源引用
}
```

### 存储层设计

```
┌─────────────────────────────────────────────────────────────┐
│  Ingestion API                                              │
│  - 校验 SourceEvent 格式                                    │
│  - 检查 idempotency_key 幂等性                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  raw_events 表                                              │
│  - 保留原始 SourceEvent（完整字段）                         │
│  - 支持溯源：source_system, source_record_key               │
│  - 支持幂等：idempotency_key（唯一约束）                    │
│  - 支持路由：dataset_key → Normalizer                       │
└─────────────────────────────────────────────────────────────┘
```

## 原因

### 1. 标准化接入

- 所有上游系统使用统一格式，降低接入成本
- 新增上游系统无需修改存储层代码
- 通过 `source_system` 字段区分不同来源

### 2. 数据可追溯

| 字段 | 用途 |
|------|------|
| `source_system` | 标识数据来源系统 |
| `source_record_key` | 关联上游原始记录 |
| `source_ref` | 上游资源定位符 |
| `collected_at` | 记录接入时间 |
| `payload` | 保留原始数据完整性 |

### 3. 幂等性保证

- `idempotency_key` 为必需字段
- 数据库层面设置唯一约束
- 重复事件自动忽略，返回成功响应

### 4. 灵活的数据路由

- `dataset_key` 用于路由到对应的 Normalizer
- 格式建议：`<source_system>.<collection_name>`
- 支持不同数据集使用不同的归一化逻辑

## 影响

### 正面影响

- 统一接入标准，降低新上游系统接入成本
- 数据完整可追溯
- 天然支持幂等性
- 与具体上游系统解耦

### 负面影响

- 上游系统需要适配 SourceEvent 格式
- 增加一层字段映射（上游格式 → SourceEvent）
- payload 为 JSON 文本，查询效率低于结构化字段

## 替代方案

### 方案 A：各上游系统自定义格式（已拒绝）

每个上游系统使用自己的数据格式接入。

**拒绝原因**：
- 接入成本高，每个系统需要单独开发适配逻辑
- 存储层需要支持多种 schema
- 无法统一做幂等性校验

### 方案 B：直接存储上游原始格式（已拒绝）

直接存储上游系统的原始 JSON，不做任何标准化。

**拒绝原因**：
- 无法统一追溯数据来源
- 幂等性难以保证
- 下游消费需要了解每种上游格式

## 相关决策

- ADR-005: 三层数据架构
- ADR-007: DCP 作为上游采集平台集成
- ADR-009: Sandbox API 下游应用接口

## 备注

- `payload` 字段保留原始数据，不做结构约束
- `dataset_key` 是 Normalizer 路由的关键字段
- 建议上游系统在推送前对 `payload` 做压缩（如大字段）
- 批量接入接口支持一次推送多条事件
