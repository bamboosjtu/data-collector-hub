# DataCollectorHub 规则

## 职责

本项目是独立的 DataHub。
拥有 schema 注册表、表批量入库、SQLite 存储、幂等处理、下载器连接器配置、API 密钥、状态 API 和面向多个下游应用的服务 API。

## 边界

- 不在本项目实现 DCP 站点登录或页面抓取。
- 不在本项目实现 DCP 协议参数、加密、Cookie、分页或风控处理。
- 不向消费者直接暴露 DCP 原始协议字段。
- 将 `downloader-dcp` 视为一个上游采集器，不是 DataHub 的一部分。
- 消费者必须通过服务 API 访问数据。

## 入库

- 在 `POST /ingestion/v1/table-batches` 校验表批量载荷。
- 使用 DataHub 拥有的表 schema，来源于插件目录 `plugins/*/tables.yaml`。
- 存储 `ingestion_jobs`、`ingestion_messages`、`table_writes`、`schema_versions` 和已注册业务表。
- 使用 `message_id`、`idempotency_key` 和 `payload_hash` 进行重复抑制和冲突检测。
- 拒绝未知表和未知列；不静默透传源字段。

## 服务

- 消费者 API 必须强制执行 API 密钥作用域。
- 查询 API 返回已注册业务表的 DTO，不返回原始 DCP 记录。
- 查询路由由插件 `plugin.yaml` 的 `query_routes` 动态注册，不手写硬编码。

## 插件

- 每个数据源对应一个插件目录（如 `plugins/dcp/`）。
- 插件通过 `plugin.yaml` 声明：连接器配置、命令（job_type + required_params）、scope 映射、查询路由。
- 插件通过 `tables.yaml` 声明：表 schema（列定义、主键、写入模式、scope 列）。
- 核心代码不包含任何数据源特定逻辑；添加新数据源只需新建插件目录。

## 存储

- 所有业务表采用 response-aligned storage：每个 API 响应对应一张独立表，字段展开为独立列。
- 不使用 `raw` JSON 字段存储业务数据；未注册的溢出字段可存入 `extra`（json 类型）。
- 写入模式由插件 `tables.yaml` 声明：`upsert`、`replace_scope`、`append`。
- scope 映射由插件 `plugin.yaml` 的 `scope_mappings` 声明，核心代码不硬编码。
