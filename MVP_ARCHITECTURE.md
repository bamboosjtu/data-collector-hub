# DataCollectorHub MVP 目标架构

> 文档状态：重构目标架构基线  
> 适用仓库：`DataCollectorHub` / `data-collector-hub`  
> 适用阶段：MVP 重构版  
> 架构模式：`core + plugin`  
> 核心入库契约：`DataHub TableBatch v1`  
> 核心存储：SQLite + response-aligned business tables

---

## 0. 文档目的

本文档是 `DataCollectorHub` 仓库重构的目标架构文档，用于指导后续代码重构、模块拆分、接口实现、测试补齐和验收。

本文档必须可独立阅读。读者不需要了解历史讨论，也不需要依赖 downloader-dcp、dcp_sdk 或旧版 deprecated 分支文档，即可理解 DataCollectorHub MVP 的目标架构。

本文档确定以下问题：

```text
1. DataCollectorHub 的 MVP 定位是什么。
2. core + plugin 的职责边界是什么。
3. connector 与 plugin 的关系是什么。
4. DCP / downloader-dcp 如何接入，但不污染 core。
5. DataHub TableBatch v1 契约归谁维护。
6. DataHub 如何触发采集、接收入库、幂等写入和提供查询。
7. MVP 阶段必须实现哪些能力，明确不做哪些能力。
8. 仓库重构后应形成怎样的模块结构。
```

本文档不是 downloader-dcp 的架构文档，也不是 dcp_sdk 的架构文档。downloader-dcp 和 dcp_sdk 是上游项目；本文只定义 DataCollectorHub 侧应实现的目标架构。

---

## 1. 项目定位

`DataCollectorHub` 是一个插件驱动的本地数据存储、摄取、调度与查询框架。

MVP 阶段，DataCollectorHub 主要接入 downloader-dcp 产出的 DCP 数据，但 DataCollectorHub 的 core 不绑定 downloader-dcp，也不绑定 DCP 协议。DCP 只是通过一个 Plugin 接入的上游数据源。

DataCollectorHub 的目标定位是：

```text
DataCollectorHub = Core Framework + Plugins
```

其中：

```text
Core Framework
  负责通用能力：插件加载、schema registry、调度、触发、TableBatch 入库、SQLite 写入、状态记录、查询 API、运维 API。

Plugins
  负责数据源或数据集相关声明：dataset、schedule、trigger、table schema、write_mode、query_routes、展示元数据。
```

DataCollectorHub 不直接访问 DCP，不调用 dcp_sdk，不处理 DCP 登录、瑞数、加密、分页、前置请求、技术参数派生等协议细节。

---

## 2. 核心设计原则

### 2.1 core 是稳定框架，plugin 是扩展声明层

MVP 架构必须以 `core + plugin` 为主线。

```text
core:
  稳定、通用、数据源无关。

plugin:
  可扩展、数据源相关、声明式优先。
```

core 不能依赖某一个具体数据源。plugin 可以声明如何对接某一个数据源或外部采集器。

### 2.2 connector 是 plugin 的一种能力，不是独立顶层架构

MVP 不引入独立于 Plugin 的 `SourceConnector` 顶层体系。

```text
正确：connector 是 plugin 的一种能力或一种 plugin kind。
错误：core + connector + plugin 三套扩展体系并存。
```

例如，DCP Plugin 可以声明自己是 external collector plugin，并包含对 downloader-dcp `/sync` 的触发配置。但 core 不应该出现 `DcpDownloaderClient`、`DcpConnector` 这类数据源特定概念。

### 2.3 TableBatch v1 是 DataCollectorHub core 的入库契约

`DataHub TableBatch v1` 是 DataCollectorHub 的入库契约，由 DataCollectorHub 仓库维护。

MVP 不建立独立 contract 仓库，不发布共享 contract package。

契约事实来源为：

```text
1. 本文档。
2. DataCollectorHub core 中的 TableBatch v1 model / schema / validator。
3. DataCollectorHub tests/fixtures 中的 TableBatch v1 样例。
4. DataCollectorHub /ingestion/v1/table-batches 的校验逻辑。
```

上游 producer 可以实现这个契约。downloader-dcp 是其中一个 producer。

### 2.4 core 不包含数据源特定逻辑

core 不应出现以下内容：

```text
dcp_sdk import
DCP pageName / apiName 硬编码
DCP roleName / provinceCode / uuid / pageSize 处理
瑞数、cookie、token、登录状态处理
downloader-dcp 专用业务流程
DCP 业务参数派生
```

core 只处理通用能力：Plugin 加载、TableBatch 校验、写入策略、SQLite 存储、状态记录、调度触发和查询路由。

### 2.5 plugin 不绕过 core

plugin 可以声明 schema、trigger、write_mode 和 query route，但不能绕过 core 直接写业务库。

```text
plugin 不直接创建业务表。
plugin 不直接执行 upsert / replace_scope / append。
plugin 不直接修改 ingestion_messages / table_writes。
plugin 不直接把 downloader 结果写入 SQLite。
```

所有入库必须经过 core 的 ingestion 和 storage 事务。

### 2.6 MVP 保持简单

MVP 使用 SQLite，不引入 Kafka、RabbitMQ、PostgreSQL、多租户权限、复杂血缘、水位表、分布式锁或跨进程插件沙箱。

MVP 重点保证：

```text
1. core 与 plugin 边界清晰。
2. 入库契约稳定。
3. 幂等接收可靠。
4. 表结构由 plugin 声明、core 执行。
5. 写入策略清晰。
6. 状态可排查。
7. 查询接口可用。
```

---

## 3. 术语定义

| 术语 | 定义 |
|---|---|
| DataCollectorHub / DataHub | 本仓库实现的本地数据枢纽。本文中二者同义。代码命名优先使用 DataCollectorHub，接口和契约中可使用 DataHub。 |
| core | DataCollectorHub 的稳定框架层，包含插件加载、registry、scheduler、ingestion、storage、API、admin 等通用模块。 |
| plugin | DataCollectorHub 的扩展单元，负责声明数据源、数据集、表结构、触发方式、查询路由和展示元数据。 |
| connector | plugin 的一种能力，表示该 plugin 能对接外部 producer 或外部数据源。不是独立顶层架构。 |
| external collector plugin | 不直接采集数据，只负责声明和触发外部采集器的 plugin。DCP Plugin 属于此类。 |
| embedded collector plugin | 插件自身执行 fetch，返回 DataItem 或内部可处理的数据。RSS / demo 插件属于此类。 |
| dataset | 一组业务上相关的数据表、触发命令和查询路由的逻辑集合。 |
| table schema | plugin 声明的本地业务表结构，包括字段、主键、索引、scope 和写入策略。 |
| TableBatch v1 | DataCollectorHub core 的入库 payload 契约。上游 producer 通过该契约向 DataHub 投递 table-oriented rows。 |
| producer | 产生 TableBatch 的上游系统。例如 downloader-dcp。 |
| ingestion job | DataHub 侧的一次采集触发或入库任务记录。 |
| ingestion message | 一次 TableBatch callback 消息。DataHub 通过 message_id / idempotency_key 幂等处理。 |
| response-aligned storage | 一类业务 API 响应对应一张本地表，响应字段尽量平铺为列。 |

---

## 4. MVP 范围

### 4.1 MVP 必须实现

```text
1. core + plugin 架构。
2. plugin 发现、元数据读取、配置加载和运行。
3. 支持至少 external_collector plugin；保留 embedded plugin 扩展点。
4. DCP plugin。
5. DCP plugin 声明 dataset、tables、write_mode、query_routes、trigger_specs。
6. DataHub TableBatch v1 入库 API。
7. TableBatch 顶层结构、table 结构和 row schema 校验。
8. SQLite 元数据表和业务表自动创建。
9. upsert / replace_scope / append 三种写入模式。
10. message_id / idempotency_key / payload_hash 幂等与冲突处理。
11. ingestion_jobs / ingestion_messages / table_writes 状态记录。
12. DataHub 主动触发 external collector plugin，例如调用 downloader-dcp /sync。
13. callback ingestion：接收 producer POST 的 TableBatch。
14. plugin 声明 query_routes，core 动态注册查询 API。
15. metadata API、health API、ingestion 状态查询 API。
16. 最小 Admin UI 或运维 API，用于排查 plugin、job、message、table_write。
17. 基础测试：plugin discovery、schema registry、TableBatch validation、idempotency、write modes、query routes。
```

### 4.2 MVP 明确不做

```text
1. 不直接请求 DCP。
2. 不实现 DCP 登录、瑞数、加密、token、cookie、session 管理。
3. 不调用 dcp_sdk。
4. 不处理 DCP 分页、前置请求、技术参数派生。
5. 不保存 DCP 原始 HTTP request trace。
6. 不保存 DCP page-level response 作为核心存储模型。
7. 不把 downloader-dcp 作为 DataHub core 的一部分。
8. 不引入独立 contract 仓库。
9. 不引入 Kafka / RabbitMQ 等外部消息队列。
10. 不做复杂血缘分析。
11. 不做通用 BI 平台。
12. 不做完整多租户权限体系。
13. 不做跨进程插件沙箱。
14. 不做分布式任务调度。
15. 不把旧版 raw_events / canonical graph 作为 MVP 主路径。
```

---

## 5. 目标架构总览

### 5.1 总体结构

```text
DataCollectorHub
├── core
│   ├── plugin_loader          # 插件发现、加载、配置解析
│   ├── registry               # 聚合 plugin 声明的 dataset/table/query/trigger
│   ├── scheduler              # 根据 plugin schedule 触发任务
│   ├── trigger_runtime        # 执行 plugin trigger，不含数据源特定逻辑
│   ├── ingestion              # TableBatch v1 校验、幂等、状态机
│   ├── storage                # SQLite DDL、事务、write modes
│   ├── query_router           # 根据 plugin query_routes 注册查询 API
│   ├── admin_api              # health / metadata / job / message / table_write
│   └── settings               # 配置
│
└── plugins
    ├── dcp                    # DCP external collector plugin
    │   ├── plugin.yaml        # plugin 元数据、trigger、schedule、query_routes
    │   └── tables.yaml        # table schema、write_mode、primary_key、indexes
    ├── rss_news               # 可选 embedded plugin
    └── demo                   # 示例 plugin
```

### 5.2 运行关系

```text
Scheduler / Manual Trigger
        ↓
core.plugin_loader
        ↓
core.registry
        ↓
plugin trigger spec
        ↓
core.trigger_runtime
        ↓
external producer，例如 downloader-dcp /sync
        ↓
producer 生成 TableBatch v1
        ↓
POST /ingestion/v1/table-batches
        ↓
core.ingestion
        ↓
core.storage
        ↓
SQLite business tables
        ↓
core.query_router / Admin API / UI
```

### 5.3 core 与 plugin 的边界

| 能力 | core | plugin |
|---|---|---|
| 插件发现与加载 | 负责 | 提供文件和元数据 |
| dataset 注册 | 聚合、校验、索引 | 声明 |
| table schema | 校验、建表、迁移检查 | 声明 |
| write_mode | 执行 | 声明 |
| 主键 / 索引 / scope | 执行建表与写入约束 | 声明 |
| schedule | 执行调度 | 声明调度计划 |
| external trigger | 执行通用 HTTP / command 调用 | 声明调用目标、参数模板 |
| downloader-dcp 细节 | 不包含 | DCP plugin 可以声明 `/sync` 调用方式 |
| TableBatch v1 校验 | 负责 | 不负责 |
| SQLite 写入 | 负责 | 不直接写库 |
| query API | 动态注册和执行 | 声明 route 与过滤规则 |
| Admin UI/API | 负责 | 提供展示元数据 |

---

## 6. Core 架构

### 6.1 core/plugin_loader

职责：

```text
1. 扫描 plugin 目录。
2. 加载 plugin.yaml / tables.yaml。
3. 可选支持 Python plugin class 的懒加载。
4. 校验 plugin metadata。
5. 输出 PluginSpec。
6. 不执行数据源业务逻辑。
```

MVP 推荐声明式优先：

```text
plugins/{plugin_id}/plugin.yaml
plugins/{plugin_id}/tables.yaml
```

保留 Python plugin class 的兼容扩展点，但 core 的关键能力不依赖 Python plugin 内部代码。

### 6.2 core/registry

职责：

```text
1. 聚合所有 plugin 的 dataset 声明。
2. 聚合所有 table schema。
3. 聚合 query_routes。
4. 聚合 trigger_specs。
5. 校验 table_name 唯一性。
6. 校验 dataset_key 与 table schema 的对应关系。
7. 生成运行时 registry。
8. 可将 registry 快照写入 schema_versions。
```

registry 是 core 与 plugin 的关键边界。

```text
plugin 只声明。
registry 负责校验和聚合。
storage 负责执行。
```

### 6.3 core/scheduler

职责：

```text
1. 读取 registry 中的 schedule 声明。
2. 创建调度任务。
3. 支持手动触发。
4. 调用 trigger_runtime 执行 plugin trigger。
5. 记录 ingestion_job。
```

MVP 可以采用进程内 scheduler。不做分布式调度。

### 6.4 core/trigger_runtime

职责：

```text
1. 根据 plugin trigger_spec 构造外部调用。
2. 支持 http_sync 类型 trigger。
3. 注入 DataHub callback URL。
4. 记录 producer 返回的 job id。
5. 更新 ingestion_job 状态。
```

trigger_runtime 必须保持通用，不能出现 DCP 特定逻辑。

例如，DCP plugin 可以声明：

```yaml
triggers:
  project_tech_full:
    type: http_sync
    method: POST
    url: "${DCP_DOWNLOADER_BASE_URL}/sync"
    request:
      job_type: project_tech_full
      params_from: input
      sink:
        type: http_callback
        url: "${DATAHUB_CALLBACK_BASE_URL}/ingestion/v1/table-batches"
```

core 只负责根据这个声明发起 HTTP 请求。

### 6.5 core/ingestion

职责：

```text
1. 提供 POST /ingestion/v1/table-batches。
2. 校验 TableBatch v1 顶层结构。
3. 校验 message_id / idempotency_key / payload_hash。
4. 校验 table_name 是否在 registry 注册。
5. 校验 rows 字段、类型、非空、主键。
6. 校验 scope_values。
7. 将合法写入请求交给 storage。
8. 记录 ingestion_messages 和 table_writes。
9. 返回明确错误码。
```

core/ingestion 不理解 DCP，只理解 TableBatch v1。

### 6.6 core/storage

职责：

```text
1. 根据 registry 创建和校验 SQLite 表。
2. 创建元数据表。
3. 执行 upsert。
4. 执行 replace_scope。
5. 执行 append。
6. 为业务表附加入库元数据列。
7. 保证每个 message 在一个事务中完成。
8. 回滚失败写入。
```

plugin 不直接调用 SQLite 执行业务写入。

### 6.7 core/query_router

职责：

```text
1. 读取 plugin query_routes。
2. 动态注册 GET 查询接口。
3. 将路径参数和查询参数转换为 SQL filters。
4. 应用 default_limit / max_limit。
5. 返回业务表数据。
```

MVP 查询 API 只查询已落库数据，不实时反向调用 downloader，也不实时访问 DCP。

### 6.8 core/admin_api

职责：

```text
1. GET /health。
2. GET /metadata。
3. GET /schemas。
4. GET /schemas/{table_name}。
5. GET /ingestion/v1/jobs。
6. GET /ingestion/v1/jobs/{ingestion_job_id}。
7. GET /ingestion/v1/messages。
8. GET /ingestion/v1/messages/{message_id}。
9. GET /ingestion/v1/table-writes。
10. GET /plugins。
```

---

## 7. Plugin 架构

### 7.1 Plugin 的定位

Plugin 是 DataCollectorHub 的扩展声明单元。

Plugin 负责描述数据源、数据集、触发方式、表结构、写入策略和查询路由。Plugin 不负责 core 的通用运行逻辑。

### 7.2 Plugin 基本结构

MVP 推荐每个 plugin 是一个目录：

```text
plugins/{plugin_id}/
  plugin.yaml
  tables.yaml
  __init__.py          # 可选
  hooks.py             # 可选，仅用于高级扩展
```

DCP plugin 示例：

```text
plugins/dcp/
  plugin.yaml
  tables.yaml
  __init__.py
```

### 7.3 plugin.yaml 职责

`plugin.yaml` 声明：

```text
1. plugin_id
2. name / version / description
3. plugin_kind
4. execution_mode
5. datasets
6. schedules
7. triggers
8. query_routes
9. display metadata
```

示例：

```yaml
plugin_id: dcp
name: DCP
version: 1.0.0
description: DCP external collector plugin
plugin_kind: external_collector
execution_mode: http_sync

datasets:
  - dataset_key: plan_year
    title: 年度计划
    description: 年度计划与进度相关数据

triggers:
  plan_year_sync:
    type: http_sync
    dataset_key: plan_year
    required_params:
      - planYear
    request:
      method: POST
      url: "${DCP_DOWNLOADER_BASE_URL}/sync"
      body:
        job_type: plan_year_sync
        params_from: input
        sink:
          type: http_callback
          url: "${DATAHUB_CALLBACK_BASE_URL}/ingestion/v1/table-batches"

schedules:
  - trigger_key: plan_year_sync
    cron: "0 7 * * *"
    enabled: false

query_routes:
  - path: /api/v1/plan/year-plan-view
    table: dcp_plan_year_plan_view
    query_filters:
      planYear: planYear
    default_limit: 100
    max_limit: 1000
```

### 7.4 tables.yaml 职责

`tables.yaml` 声明业务表：

```text
1. table_name
2. dataset_key
3. columns
4. primary_key
5. write_mode
6. scope_column_names
7. indexes
8. unknown_field_policy
9. display metadata
```

示例：

```yaml
tables:
  - table_name: dcp_plan_year_plan_view
    dataset_key: plan_year
    title: 年度计划视图
    write_mode: upsert
    primary_key:
      - planYear
      - id
    scope_column_names:
      - planYear
    columns:
      - name: planYear
        type: TEXT
        nullable: false
      - name: id
        type: TEXT
        nullable: false
      - name: prjCode
        type: TEXT
        nullable: true
      - name: prjName
        type: TEXT
        nullable: true
      - name: jhkgTime
        type: TEXT
        nullable: true
      - name: jhtcTime
        type: TEXT
        nullable: true
    indexes:
      - columns: [planYear]
      - columns: [prjCode]
    unknown_field_policy: capture_extra
```

### 7.5 Plugin 类型

MVP 支持以下 plugin_kind：

| plugin_kind | 说明 | MVP 状态 |
|---|---|---|
| external_collector | 控制外部采集器，不直接采集。DCP plugin 属于此类。 | 必须支持 |
| embedded_collector | 插件自身执行 fetch。RSS / demo 可属于此类。 | 保留兼容 |
| dataset | 仅声明 dataset/table/query，不负责触发。 | 可选 |

### 7.6 DCP Plugin 职责

DCP Plugin 负责：

```text
1. 声明 DCP 相关 dataset_key。
2. 声明 DCP response-aligned tables。
3. 声明 write_mode、primary_key、scope、indexes。
4. 声明 DataHub 如何触发 downloader-dcp /sync。
5. 声明 query_routes。
6. 声明展示元数据。
```

DCP Plugin 不负责：

```text
1. DCP 登录。
2. 瑞数。
3. 加密。
4. 分页。
5. 前置请求。
6. 参数派生。
7. 调用 dcp_sdk。
8. 写 SQLite。
```

---

## 8. TableBatch v1 入库契约

### 8.1 归属

TableBatch v1 是 DataCollectorHub core 的入库契约。

```text
DataCollectorHub core owns:
  - /ingestion/v1/table-batches
  - TableBatch v1 validation
  - idempotency rules
  - write transaction rules

downloader-dcp implements:
  - a DataHub-compatible TableBatch producer
```

MVP 不建立第三方 contract 仓库。

### 8.2 Endpoint

```text
POST /ingestion/v1/table-batches
```

### 8.3 Payload

```json
{
  "message_id": "msg_001",
  "idempotency_key": "idem_001",
  "downloader_job_id": "job_progress_2026",
  "collect_run_id": "collect_progress_2026",
  "dataset_key": "plan_year",
  "scope_key": "planYear:2026",
  "payload_hash": "sha256:...",
  "tables": [
    {
      "table_name": "dcp_plan_year_plan_view",
      "scope_values": {
        "planYear": "2026"
      },
      "rows": [
        {
          "planYear": "2026",
          "id": "row_001",
          "prjCode": "1716A121004B",
          "prjName": "测试项目"
        }
      ]
    }
  ]
}
```

### 8.4 顶层字段

| 字段 | 必填 | 说明 |
|---|---|---|
| message_id | 是 | producer 生成的消息 ID，用于幂等。 |
| idempotency_key | 是 | 幂等键，通常与 producer job / collect / batch 相关。 |
| downloader_job_id | 是 | 上游 producer job ID。MVP 保留该字段名以兼容 downloader-dcp。 |
| collect_run_id | 是 | 上游 collect run ID。 |
| dataset_key | 是 | 本批数据所属 dataset。必须由 plugin 注册。 |
| scope_key | 否 | 人类可读的 scope 标识。 |
| payload_hash | 是 | payload 内容 hash，用于冲突检测。 |
| tables | 是 | table batch 数组。 |

说明：MVP 为保持简洁，不额外引入 `contract_version`、`source_key`、`schema_version`。版本由 endpoint `/ingestion/v1` 表达。

### 8.5 table 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| table_name | 是 | 目标业务表名，必须在 registry 中注册。 |
| scope_values | 是 | 当前 table 的 scope 值。upsert 可为空对象，replace_scope 必须包含 scope 字段。 |
| rows | 是 | 行数据数组。 |

---

## 9. Ingestion 流程

### 9.1 callback ingestion 流程

```text
1. 接收 POST /ingestion/v1/table-batches。
2. 校验 message_id / idempotency_key / payload_hash。
3. 检查幂等状态。
4. 校验 dataset_key 是否注册。
5. 校验 tables 数组。
6. 校验 table_name 是否注册。
7. 校验 table 是否属于 dataset_key。
8. 校验 rows 字段、类型、nullable、primary_key。
9. 校验 scope_values。
10. 在同一事务中写入业务表和元数据表。
11. 更新 ingestion_messages 为 succeeded。
12. 更新 ingestion_jobs 聚合状态。
13. 返回成功或明确错误。
```

### 9.2 sync trigger 流程

```text
1. 用户或 scheduler 请求触发某个 trigger_key。
2. core 查询 registry，找到 plugin trigger_spec。
3. core 校验 required_params。
4. core 创建 ingestion_job。
5. core.trigger_runtime 根据 trigger_spec 构造外部请求。
6. 对 DCP plugin，外部请求是 POST downloader-dcp /sync。
7. core 注入 sink.url = DataHub /ingestion/v1/table-batches。
8. producer 返回 accepted 和 downloader_job_id。
9. core 更新 ingestion_job 状态。
10. 后续由 producer callback TableBatch 入库。
```

### 9.3 query 流程

```text
1. core 启动时读取 plugin query_routes。
2. core.query_router 动态注册查询路由。
3. 用户请求查询 API。
4. core 将 path_filters / query_filters 转换为 SQL WHERE。
5. core 查询 SQLite business tables。
6. 返回业务数据。
```

查询 API 不反向调用 downloader-dcp，不实时访问 DCP。

---

## 10. 写入模式

### 10.1 upsert

用于主键稳定的业务实体表。

规则：

```text
1. 必须定义 primary_key。
2. 根据 primary_key 执行 INSERT ON CONFLICT DO UPDATE。
3. 重复接收同一 message_id 时不重复写入。
4. 更新 _ingest_updated_at。
```

### 10.2 replace_scope

用于某个 scope 下的快照型数据。

规则：

```text
1. 必须定义 scope_column_names。
2. table batch 必须提供 scope_values。
3. 写入时先删除同 scope 旧数据。
4. 再写入本次 rows。
5. 删除和写入必须在同一事务中完成。
6. 重复接收同一 message_id 时不重复执行 replace。
```

MVP 不引入 watermark。旧快照覆盖新快照的问题暂由调度和 producer 保证，后续版本再扩展。

### 10.3 append

用于事件流或历史记录。

规则：

```text
1. 不覆盖旧数据。
2. 每行自动补充 _ingest_message_id 和 _ingest_row_index。
3. 设置 UNIQUE(_ingest_message_id, _ingest_row_index)。
4. 重复接收同一 message_id 时不重复插入。
```

---

## 11. SQLite 数据模型

### 11.1 元数据表

MVP 保留少量元数据表。

```text
ingestion_jobs       # DataHub 侧触发任务和上游 job 映射
ingestion_messages   # TableBatch 消息幂等和冲突检测
table_writes         # 每张表写入统计和错误
schema_versions      # registry 快照
api_keys             # 可选 API key 管理
plugins              # 可选，持久化 plugin metadata 和启用状态
```

### 11.2 ingestion_jobs

```sql
CREATE TABLE ingestion_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ingestion_job_id TEXT NOT NULL UNIQUE,
  plugin_id TEXT,
  trigger_key TEXT,
  downloader_job_id TEXT UNIQUE,
  dataset_key TEXT,
  params_json TEXT NOT NULL,
  status TEXT NOT NULL,
  message_total INTEGER DEFAULT 0,
  message_received INTEGER DEFAULT 0,
  message_failed INTEGER DEFAULT 0,
  row_count INTEGER DEFAULT 0,
  producer_status_json TEXT,
  result_json TEXT,
  error TEXT,
  started_at TEXT,
  finished_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 11.3 ingestion_messages

```sql
CREATE TABLE ingestion_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id TEXT NOT NULL UNIQUE,
  idempotency_key TEXT NOT NULL UNIQUE,
  ingestion_job_id TEXT,
  downloader_job_id TEXT,
  collect_run_id TEXT,
  dataset_key TEXT NOT NULL,
  scope_key TEXT,
  payload_hash TEXT NOT NULL,
  status TEXT NOT NULL,
  table_count INTEGER DEFAULT 0,
  row_count INTEGER DEFAULT 0,
  error_code TEXT,
  error TEXT,
  received_at TEXT DEFAULT CURRENT_TIMESTAMP,
  written_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 11.4 table_writes

```sql
CREATE TABLE table_writes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id TEXT NOT NULL,
  table_name TEXT NOT NULL,
  dataset_key TEXT,
  scope_values_json TEXT,
  write_mode TEXT NOT NULL,
  status TEXT NOT NULL,
  row_count INTEGER DEFAULT 0,
  inserted_count INTEGER DEFAULT 0,
  updated_count INTEGER DEFAULT 0,
  deleted_count INTEGER DEFAULT 0,
  error_code TEXT,
  error TEXT,
  started_at TEXT,
  finished_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 11.5 schema_versions

```sql
CREATE TABLE schema_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  schema_version TEXT NOT NULL UNIQUE,
  registry_json TEXT NOT NULL,
  checksum TEXT NOT NULL,
  active INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 11.6 业务表通用入库元数据列

每张业务表由 plugin `tables.yaml` 声明，core.storage 动态生成 DDL。业务表自动附加以下入库元数据列：

```text
_ingest_message_id    TEXT
_ingest_job_id        TEXT
_downloader_job_id    TEXT
_collect_run_id       TEXT
_ingest_row_index     INTEGER
_ingest_payload_hash  TEXT
_ingest_created_at    TEXT DEFAULT CURRENT_TIMESTAMP
_ingest_updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
_extra                TEXT NULL
```

其中：

```text
append 表对 (_ingest_message_id, _ingest_row_index) 建唯一约束。
upsert / replace_scope 表根据业务 primary_key 建唯一约束。
unknown_field_policy = capture_extra 时，未声明字段写入 _extra JSON。
```

---

## 12. 幂等与错误处理

### 12.1 幂等键

```text
message_id
idempotency_key
payload_hash
```

### 12.2 幂等规则

```text
1. message_id 未出现过 → 正常处理。
2. message_id 已成功处理且 payload_hash 相同 → 返回 duplicate_accepted，HTTP 2xx。
3. message_id 已成功处理但 payload_hash 不同 → 返回 payload_hash_conflict，HTTP 409。
4. idempotency_key 已存在但 message_id 不同 → 返回 idempotency_conflict，HTTP 409。
5. message_id 曾失败且 payload_hash 相同 → 允许重试。
6. message_id 曾失败但 payload_hash 不同 → 返回 payload_hash_conflict，HTTP 409。
```

### 12.3 错误码

| 错误场景 | error_code | HTTP |
|---|---|---|
| payload 格式错误 | invalid_batch | 400 |
| 缺少必填字段 | missing_required_field | 422 |
| 未注册 dataset_key | unknown_dataset | 422 |
| 未注册 table_name | unknown_table | 422 |
| table 不属于 dataset | table_dataset_mismatch | 422 |
| schema mismatch | schema_mismatch | 422 |
| 缺少 primary_key 字段 | missing_primary_key | 422 |
| 缺少 scope_values | missing_scope_values | 422 |
| payload_hash 冲突 | payload_hash_conflict | 409 |
| idempotency_key 冲突 | idempotency_conflict | 409 |
| 数据库写入失败 | storage_error | 500 |

### 12.4 与 producer 重试的关系

producer 可以使用 at-least-once delivery。DataHub 必须保证幂等。

```text
成功写入或重复成功消息 → 返回 2xx。
schema mismatch 等可修复错误 → 返回非 2xx，producer 可重试。
payload_hash_conflict / idempotency_conflict → 返回 409，表示不可自动重试。
```

---

## 13. HTTP API

### 13.1 基础 API

```text
GET /health
GET /metadata
GET /plugins
GET /schemas
GET /schemas/{table_name}
```

### 13.2 触发 API

```text
POST /ingestion/v1/jobs
GET  /ingestion/v1/jobs
GET  /ingestion/v1/jobs/{ingestion_job_id}
```

`POST /ingestion/v1/jobs` 用于通过 plugin trigger 发起采集。

示例：

```json
{
  "plugin_id": "dcp",
  "trigger_key": "plan_year_sync",
  "params": {
    "planYear": "2026"
  }
}
```

响应：

```json
{
  "ingestion_job_id": "ing_plan_year_2026_abc123",
  "downloader_job_id": "job_plan_year_2026_abc123",
  "status": "accepted"
}
```

### 13.3 入库 API

```text
POST /ingestion/v1/table-batches
GET  /ingestion/v1/messages
GET  /ingestion/v1/messages/{message_id}
GET  /ingestion/v1/table-writes
```

### 13.4 查询 API

查询 API 由 plugin `query_routes` 动态注册。

示例：

```text
GET /api/v1/plan/year-plan-view?planYear=2026
GET /api/v1/plan/progress-management?planYear=2026
GET /api/v1/safety/daily-meetings?dateRange=2026-06-01..2026-06-04
```

MVP 查询 API 只查询本地已入库数据。

---

## 14. DCP 与 downloader-dcp 集成

### 14.1 职责边界

```text
DataCollectorHub core:
  - 加载 DCP plugin。
  - 聚合 DCP plugin 的 table schema。
  - 根据 DCP plugin trigger_spec 发起通用外部调用。
  - 接收 TableBatch v1。
  - 校验、幂等、写 SQLite。
  - 提供查询。

DCP plugin:
  - 声明 dataset。
  - 声明 table schema。
  - 声明 write_mode / primary_key / scope。
  - 声明如何调用 downloader-dcp /sync。
  - 声明 query_routes。

downloader-dcp:
  - 接收 /sync。
  - 登录 DCP。
  - 管理会话。
  - 调用 dcp_api / dcp_sdk。
  - 处理分页、前置请求、参数派生。
  - 生成 TableBatch v1。
  - 通过 http_callback 投递 DataHub。
```

### 14.2 集成流程

```text
DataHub Scheduler / Manual Trigger
        ↓
core.registry 找到 dcp plugin trigger_spec
        ↓
core.trigger_runtime POST downloader-dcp /sync
        ↓
downloader-dcp 执行采集
        ↓
downloader-dcp 生成 TableBatch v1
        ↓
downloader-dcp callback POST DataHub /ingestion/v1/table-batches
        ↓
core.ingestion 校验、幂等、写入
        ↓
SQLite business tables
        ↓
Query API / Admin UI
```

### 14.3 禁止路径

以下路径不属于 MVP 正式入库路径：

```text
DataHub 拉取 downloader job result records 后自行展开入库。
DataHub 读取 downloader 本地文件后自行解析入库。
DCP plugin 直接写 SQLite。
downloader-dcp 直接写 DataHub SQLite。
core 直接调用 dcp_sdk。
```

正式入库路径只有：

```text
producer → TableBatch v1 → /ingestion/v1/table-batches → core.ingestion → core.storage
```

---

## 15. Response-aligned Storage

### 15.1 原则

业务表采用 response-aligned storage：

```text
1. 一个稳定业务 API / 响应结构对应一张本地表。
2. 响应中的主要字段展开为表字段。
3. 不以 raw JSON 作为主要业务查询模型。
4. 未注册字段可按 unknown_field_policy 写入 _extra。
5. 表结构、主键、索引、写入模式由 plugin 声明。
6. 表创建、校验、写入由 core 执行。
```

### 15.2 DCP MVP 表

MVP 的 DCP 表清单由 `plugins/dcp/tables.yaml` 决定。建议初始包含年度计划、安全站班会等当前下游明确需要的数据集。

示例：

| 表名 | 来源 | 主键 | 写入模式 |
|---|---|---|---|
| dcp_plan_year_plan_view | plan.yearPlanView | planYear, id | upsert |
| dcp_plan_progress_management | plan.progressManagement | planYear, id | upsert |
| dcp_year_progress_project_domain | plan.yearPlanView derived | year, id | replace_scope |
| dcp_safety_daily_meeting | safe.dailyMeeting | dateRange, id | upsert |

完整表清单不硬编码在 core 中。

---

## 16. 仓库重构目标结构

建议重构后的目录结构：

```text
DataCollectorHub/
├── src/
│   └── datahub/
│       ├── app.py
│       ├── settings.py
│       │
│       ├── core/
│       │   ├── plugin_loader.py
│       │   ├── registry.py
│       │   ├── scheduler.py
│       │   ├── trigger_runtime.py
│       │   └── errors.py
│       │
│       ├── ingestion/
│       │   ├── models.py
│       │   ├── validator.py
│       │   ├── service.py
│       │   └── idempotency.py
│       │
│       ├── storage/
│       │   ├── sqlite.py
│       │   ├── ddl.py
│       │   ├── writer.py
│       │   └── migrations.py
│       │
│       ├── api/
│       │   ├── metadata.py
│       │   ├── ingestion.py
│       │   ├── query.py
│       │   ├── health.py
│       │   └── plugins.py
│       │
│       └── admin/
│           └── views.py
│
├── plugins/
│   ├── dcp/
│   │   ├── plugin.yaml
│   │   ├── tables.yaml
│   │   └── __init__.py
│   ├── rss_news/
│   │   ├── plugin.yaml
│   │   └── __init__.py
│   └── demo/
│       ├── plugin.yaml
│       └── __init__.py
│
├── tests/
│   ├── fixtures/
│   │   └── table_batch_v1/
│   ├── test_plugin_loader.py
│   ├── test_registry.py
│   ├── test_table_batch_validation.py
│   ├── test_idempotency.py
│   ├── test_write_modes.py
│   └── test_query_routes.py
│
├── docs/
│   └── MVP_ARCHITECTURE.md
│
└── pyproject.toml
```

---

## 17. 重构实施顺序

建议按以下顺序重构：

### 阶段 1：core 骨架

```text
1. 建立 src/datahub 包结构。
2. 实现 settings。
3. 实现 plugin_loader。
4. 实现 registry。
5. 定义 PluginSpec / TableSpec / TriggerSpec / QueryRouteSpec。
6. 编写 plugin_loader 和 registry 测试。
```

### 阶段 2：storage 与 schema

```text
1. 实现 SQLite 连接和事务封装。
2. 实现元数据表 DDL。
3. 实现业务表 DDL 生成。
4. 实现 upsert / replace_scope / append。
5. 编写 write_modes 测试。
```

### 阶段 3：TableBatch ingestion

```text
1. 定义 TableBatch v1 models。
2. 实现 validator。
3. 实现 idempotency。
4. 实现 ingestion service。
5. 实现 POST /ingestion/v1/table-batches。
6. 编写 TableBatch fixtures 和测试。
```

### 阶段 4：DCP plugin

```text
1. 创建 plugins/dcp/plugin.yaml。
2. 创建 plugins/dcp/tables.yaml。
3. 将年度计划、安全站班会等 MVP 表放入 tables.yaml。
4. 声明 downloader-dcp /sync trigger。
5. 声明 query_routes。
6. 验证 registry 聚合结果。
```

### 阶段 5：trigger 与 scheduler

```text
1. 实现 trigger_runtime。
2. 实现 POST /ingestion/v1/jobs。
3. 实现 scheduler。
4. 打通 DataHub → downloader-dcp /sync → callback ingestion。
```

### 阶段 6：query 与 admin

```text
1. 实现 query_router。
2. 实现 metadata / schemas / plugins API。
3. 实现 jobs / messages / table-writes 查询 API。
4. 实现最小 Admin UI 或保留 API 优先。
```

---

## 18. 验收标准

MVP 重构完成后，必须满足：

```text
1. core 中没有 DCP 协议逻辑。
2. core 中没有 dcp_sdk import。
3. core 中没有 downloader-dcp 专用业务分支。
4. DCP 相关配置集中在 plugins/dcp。
5. 删除或停用 DCP plugin 后，core 仍可启动。
6. 新增 plugin 不需要修改 core 代码。
7. TableBatch v1 fixture 能通过 validation。
8. 重复 message_id + 相同 payload_hash 返回 duplicate_accepted。
9. 重复 message_id + 不同 payload_hash 返回 conflict。
10. upsert / replace_scope / append 均有自动化测试。
11. query_routes 能动态注册并查询 SQLite。
12. DataHub 能触发 downloader-dcp /sync 并接收 callback 入库。
13. ingestion_jobs / ingestion_messages / table_writes 可用于排查失败。
```

---

## 19. 架构摘要

DataCollectorHub MVP 的目标架构是：

```text
core + plugin
```

核心判断：

```text
1. core 是稳定框架，plugin 是扩展声明层。
2. connector 是 plugin 的一种能力，不是独立顶层架构。
3. TableBatch v1 是 DataCollectorHub core 的入库契约。
4. downloader-dcp 是外部 producer，不是 core 依赖。
5. DCP 通过 plugins/dcp 接入。
6. 所有正式入库都经过 /ingestion/v1/table-batches。
7. 所有业务表由 plugin 声明，core 创建、校验和写入。
8. MVP 保持 SQLite、本地部署、简单元数据表和明确状态模型。
```

最终边界：

```text
dcp_sdk:
  负责 DCP 业务访问。

downloader-dcp:
  负责采集、分页、参数派生、TableBatch 生成和 callback 投递。

DataCollectorHub core:
  负责 plugin 加载、registry、trigger、TableBatch ingestion、SQLite 写入、状态和查询。

DataCollectorHub plugin:
  负责数据源和数据集相关声明，包括 trigger、schema、write_mode、query_routes。
```

---

## 20. 验收标准定义

### 20.1 三级验收定义

| 验收级别 | 定义 | 说明 |
|---|---|---|
| 结构验收 | 表结构、DDL、schema 注册、API 路由正确 | 不依赖 downloader 可达 |
| 调度验收 | command 触发链路、fan-out 分片、父子关联正确 | 不依赖 downloader 可达，502/failed 可接受 |
| 真实数据入库验收 | downloader 可达时，业务表有数据或明确返回无数据 | 需要 downloader-dcp 运行 |

### 20.2 结构验收标准

```text
1. normalizer source_table 不作为业务表持久化。
2. 业务表均无 raw 字段。
3. extra 只保存未声明字段，不保存完整 raw。
4. core 无数据源特定业务逻辑硬编码。
5. 所有表 schema 由 plugin tables.yaml 声明，core 不硬编码。
```

### 20.3 调度验收标准

```text
1. command 全部注册且可触发。
2. downloader_sync / fan_out / date_range_fan_out 三种 trigger 类型正确路由。
3. auto_params 正确解析日期占位符。
4. fan-out 父子任务关联（parent_job_id）可查询。
5. 子任务可独立重试。
```

### 20.4 真实数据入库验收标准

```text
1. downloader 可达时，单项目 command 返回 202 且业务表有数据。
2. fan-out command 逐项目触发，每个 projectCode 独立记录成功/失败。
3. date_range_fan_out 按日期切片，每个切片独立 job。
4. 失败项目/日期段可单独重试。
```

当前 DCP Plugin MVP 验收记录见 [docs/devlog/2026-06-06-dcp-plugin-mvp-validation.md](docs/devlog/2026-06-06-dcp-plugin-mvp-validation.md)。
