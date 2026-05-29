# 集成

downloader-dcp 是独立的采集编排器，不绑定任何特定下游系统。

- **collect 机制**：独立运行，采集并以 JSON 存储到本地，无需任何外部系统。
- **sync 机制**：采集并通过 outbox 投递到下游，下游可以是 DataHub、任意 HTTP 服务或脚本。

---

## 一、sync 集成模式

### 1.1 通用流程

```text
调用方（任意系统）
  -> POST downloader /sync，传入 job_type、params、sink
  -> 返回 { downloader_job_id, status: "accepted" }

downloader 后台执行
  -> 从 YAML 注册表校验 job_type
  -> planner 将 job_type 展开为 collect 任务
  -> executor 调用 dcp_api
  -> dcp_api 自动处理分页、参数派生、前置请求
  -> 展开 response schema → 生成 table batch
  -> 根据 sink 类型输出：
     - local_file：写本地 JSON
     - http_callback：写入 delivery_outbox，由 dispatcher 投递到下游

调用方
  -> 轮询 GET /sync/jobs/{downloader_job_id}
  -> 获取采集进度和投递进度
```

### 1.2 术语层次

- **外部集成**使用 `handler` / `dataset_key`：调用方通过 `dataset_key` 找到对应 handler。
- **内部组件**使用 `executor` / `collect_key`：planner 将 `job_type` 展开为 `collect_key` 任务，由 executor 执行。
- 两者不矛盾，是同一机制在不同抽象层次的表述。

### 1.3 sync 请求

`POST /sync`

```json
{
  "downloader_job_id": "job_project_tech_1616B0220001_20260528",
  "job_type": "project_tech_full",
  "params": {
    "projectCode": "1616B0220001"
  },
  "sink": {
    "type": "http_callback",
    "url": "http://datahub.example.com/ingestion/v1/table-batches"
  },
  "debug": false
}
```

`downloader_job_id` 可选，未传入时由 downloader 自动生成。

### 1.4 sync 响应

```json
{
  "downloader_job_id": "job_project_tech_1616B0220001_20260528",
  "status": "accepted"
}
```

---

## 二、outbox 投递机制

sync 使用 `http_callback` 时，downloader 通过 **Transactional Outbox** 模式将 table batch 投递到下游。采集与投递解耦，保证采集结果不丢失。

### 2.1 核心流程

```text
采集完成 → 生成 TableBatch
  → HttpCallbackSink.enqueue()
    → 写入 delivery_outbox 表（status=pending, callback_url=请求级URL）
  → 触发 dispatcher.dispatch_now()（即时投递，减少延迟）

后台调度 dispatch_loop（间隔 10s）：
  → requeue_stale_delivering()（回收超时行）
  → claim_pending()（条件领取，防并发重复领取）
  → 解析 payload + 读取 callback_url
  → httpx.post(callback_url, payload)
  → 成功：mark_delivered / 失败：mark_retry（渐进退避）或 mark_failed
```

### 2.2 outbox 状态机

```text
pending ──claim──> delivering ──POST 成功──> delivered
   ↑                  │
   │                  └──POST 失败──> pending（退避后重试）
   │                                     │
   │                                     └──超过重试上限──> failed
   │
   └──requeue_stale──delivering 超时 300s──┘
```

| 状态 | 含义 |
|------|------|
| `pending` | 等待投递，退避时间过后可被领取 |
| `delivering` | 已被领取，正在投递中 |
| `delivered` | 投递成功（下游返回 2xx） |
| `failed` | 投递失败且超过重试上限 |

### 2.3 投递语义：at-least-once

- 新的回调消息以 `pending` 状态插入，使用 `INSERT OR IGNORE` 保证 `message_id` 和 `idempotency_key` 唯一。
- dispatcher 通过条件领取（`claim_pending`）在同一事务内 SELECT + UPDATE，防止并发重复领取。
- 可能出现重复投递（如 delivering 超时回收后重投）；**下游必须通过 `message_id` 或 `idempotency_key` 保证幂等性**。

### 2.4 退避重试策略

| 失败次数 | 重试间隔 |
|----------|----------|
| 第 1 次 | 10 秒 |
| 第 2 次 | 30 秒 |
| 第 3 次 | 2 分钟 |
| 第 4 次 | 5 分钟 |
| 第 5 次及以后 | 15 分钟 |

超过重试上限后标记为 `failed`，不再重试。

### 2.5 callback_url 优先级

1. **行级 callback_url**：来自 `/sync` 请求的 `sink.url`，每条 outbox 消息独立存储。
2. **服务级 default_callback_url**：来自 CLI `--callback-url` 参数。
3. 两者都为空时，直接 `mark_failed`。

### 2.6 超时回收

`delivering` 状态超过 300 秒的行会被 `requeue_stale_delivering()` 重置为 `pending`，防止因进程崩溃导致的死锁行。每次 `dispatch_once()` 执行前都会先回收。

### 2.7 下游幂等处理

- 已成功 `message_id` 返回 2xx → downloader 标记 delivered。
- schema mismatch 返回非 2xx → downloader outbox 保留消息并重试。
- 修复下游 schema 后，同一 message 可重试成功。

### 2.8 明确不兼容

outbox 投递不再使用：

- `/ingestion/v1/batch`
- `ingestion.batch.v1`
- `raw_events`
- `command_key`
- `command_run_id`
- Envelope JSON 作为 HTTP 集成契约

---

## 三、table batch 载荷

dispatcher 投递到下游的载荷结构：

```json
{
  "message_id": "msg_xxx",
  "idempotency_key": "job:collect:1",
  "downloader_job_id": "job_project_tech_1616B0220001_20260528",
  "collect_run_id": "collect_tower_by_subprojectcode_xxx",
  "dataset_key": "tower",
  "scope_key": "singleProjectCode:1616B022000106",
  "payload_hash": "sha256:...",
  "tables": [
    {
      "table_name": "dcp_tower",
      "scope_values": {
        "singleProjectCode": "1616B022000106"
      },
      "rows": []
    }
  ]
}
```

下游负责表结构、写入模式、主键、索引和校验。Downloader 不创建或修改下游的存储结构。

---

## 四、DataHub 集成

DataHub 是 downloader-dcp 的典型下游，通过 outbox 接收 table batch。

### 4.1 集成流程

```text
DataHub Scheduler / Manual Trigger
        ↓
DataHub Plugin
  - 定义 schedule
  - 定义 dataset
  - 定义 table schema
  - 定义调用 downloader 的 command
        ↓
POST downloader-dcp /sync
  sink.url 指向 DataHub /ingestion/v1/table-batches
        ↓
downloader-dcp
  - 根据 dataset_key 找 handler
  - 根据简单业务参数调用 dcp_api
  - dcp_api 自动处理分页、参数派生、前置请求
  - 展开 response schema → 生成 table batch
  - 写入 delivery_outbox（pending）
        ↓
outbox dispatcher
  - claim_pending → POST DataHub /ingestion/v1/table-batches
  - 成功：delivered / 失败：退避重试
        ↓
DataHub
  - 校验 table batch schema
  - 幂等写入 SQLite（upsert / replace_scope / append）
  - 记录 ingestion 状态
        ↓
DataHub UI / API
```

### 4.2 DataHub 职责

```text
负责：
  - 插件注册（plugin.yaml + tables.yaml）
  - 表 schema 管理（权威定义在 DataHub 侧）
  - 触发 downloader sync（POST /sync）
  - 接收 table batch 并校验（POST /ingestion/v1/table-batches）
  - 幂等写入 SQLite（upsert / replace_scope / append）
  - 保存 ingestion 状态
  - 提供查询和排查 API

不负责：
  - DCP 登录、加密、瑞数
  - 采集执行逻辑
  - 业务参数补全
```

### 4.3 DataHub 幂等契约

DataHub 作为 outbox 下游，必须满足：

- 对同一 `message_id` 的重复 POST 返回 2xx（幂等）。
- 通过 `idempotency_key` 去重，不产生重复数据。
- schema 校验失败返回非 2xx，downloader 将退避重试。

---

## 五、账号池配置

sync 支持多账号并发，配置格式如下：

```json
{
  "schema_version": "account_pool_config.v1",
  "account_pool": {
    "name": "dcp_default",
    "max_workers": 3,
    "lease_timeout_seconds": 300,
    "default_cooldown_seconds": 60,
    "max_consecutive_failures": 5
  },
  "accounts": [
    {
      "account_key": "dcp_account_1",
      "enabled": true,
      "username_env": "DCP_USERNAME_1",
      "password_env": "DCP_PASSWORD_1",
      "max_workers": 1
    }
  ]
}
```

凭据通过环境变量名引用，不存储明文。

---

## 六、多项目上下文

downloader-dcp 不对外部项目有隐式依赖，自行定义其接口契约。以下上下文仅供参考。

### 6.1 项目职责边界

| 项目 | 定位 | 与 downloader-dcp 的关系 |
|------|------|--------------------------|
| dcp_sdk | DCP 业务访问 SDK | downloader 的上游依赖，提供 dcp_api |
| downloader-dcp | 独立采集编排器 | 本项目 |
| DataCollectorHub | 数据中心 | downloader 的下游，通过 outbox 接收 table batch |
| vibe-monitor | 数字沙盘消费端 | 通过 DataHub 间接消费 downloader 产出的数据 |
| dcp_lite_app | DCP 桌面应用 | dcp_sdk 的另一个下游消费者，与 downloader 无直接关系 |

### 6.2 项目间依赖关系

```text
rs-env-demo (瑞数补环境技术基础)
      │
      ▼
dcp_sdk (DCP 业务访问 SDK)
    ┌──────┴──────┐
    │             │
    ▼             ▼
downloader-dcp  dcp_lite_app
(采集编排器)    (桌面应用)
    │
    ▼ outbox 投递
DataCollectorHub (数据中心)
    │
    ▼
vibe-monitor (数字沙盘)
```

### 6.3 关键边界约束

1. **dcp_sdk 是封闭 SDK**：下游只能调用 `dcp_api` 的稳定接口，不得导入 `dcp_transport` 或 `dcp_api` 内部模块。
2. **downloader-dcp 是独立采集编排器**：不定义下游表结构、不写下游数据库、不做业务去重。DCP 技术参数在调用 `dcp_api` 前必须被拒绝。不对外部项目有隐式依赖。
3. **DataCollectorHub 是数据中心**：不实现 DCP 登录/加密/瑞数，通过 outbox 接收 downloader 产出的 table batch。表 schema 权威定义在 DataHub 侧。
4. **vibe-monitor 是纯消费端**：不依赖 DCP 原始字段名，通过 DataHub Domain API 获取数据。
