# SQLite Single-Writer 技术债务分析与解决方案

## 一、问题描述

| 编号 | 技术债务 | 影响范围 | 严重度 |
|---|---|---|---|
| 3 | SQLite MVP: single-writer, no concurrent access | Local dev only | Medium |

SQLite WAL 模式允许读写并发，但**写者之间仍然串行**。当前项目有多个后台线程并发写入 SQLite，完全依赖 `busy_timeout=30s` 排队等待写锁。在高并发场景下，长事务持有写锁会阻塞所有其他写入者，导致延迟升高甚至 `database is locked` 错误。

## 二、当前并发写入者

| 写入者 | 线程 | 频率 | 事务特征 |
|---|---|---|---|
| callback ingestion | `asyncio.to_thread` 线程池 | 随请求到达 | **长事务**：幂等检查 + 多表写入 + 元数据更新 |
| fanout scheduler | `hub-fanout-scheduler` | 每 3s tick | 10+ 次短连接写操作 |
| status poller | `hub-status-poller` | 每 5s tick | 批量 `mark_job()` 短写 |
| plugin handler | `plugin-handler-*` | 随触发请求 | `create_fanout_run_with_items` + `mark_job` |

## 三、核心瓶颈

### 3.1 ingest_table_batch 长事务（最严重）

`src/datahub/ingestion/service.py` 中，一个事务包含：

```text
BEGIN
  INSERT ingestion_messages (writing)
  SELECT ingestion_jobs (job_id_for_producer)
  对每个 table:
    write_table (DELETE + 逐行 INSERT/UPSERT)
    INSERT table_writes
  UPDATE ingestion_messages (succeeded)
  UPDATE ingestion_jobs (running)
COMMIT
```

当 payload 包含多表多行时，事务可能持续数秒，期间持有写锁阻塞所有其他写入者。

### 3.2 asyncio.to_thread 允许并发排队

`src/datahub/api/ingestion.py` 使用默认 ThreadPoolExecutor（最大 32 线程），多个回调请求并发执行 `ingest_table_batch`，但 SQLite 只允许一个写者，其余全部 busy_wait。

### 3.3 deferred 事务潜在死锁

`ingest_table_batch` 使用 `conn.execute("BEGIN")`（deferred 隔离级别），两个并发事务可能先读后写，导致 `SQLITE_BUSY` 死锁：

```text
事务 A: BEGIN → SELECT (无锁) → 尝试 INSERT (等写锁)
事务 B: BEGIN → SELECT (无锁) → 尝试 INSERT (等写锁)
→ 互相等待，直到 busy_timeout 耗尽
```

### 3.4 PRAGMA synchronous=FULL 未优化

WAL 模式下 `synchronous=NORMAL` 性能更好且安全性足够（不会损坏数据库，只在断电时可能丢失最近几个事务）。当前默认 FULL 每次写操作都 fsync。

### 3.5 fanout scheduler tick 写操作碎片化

一次 tick 内 10+ 次独立短连接写操作（claim、reset、update、skip、close 等），频繁获取/释放锁，效率低。

## 四、影响评估

| 场景 | 当前影响 | 触发条件 |
|---|---|---|
| 回调写入延迟 | 多个回调同时到达时排队等锁，P99 延迟升高 | 并发 fan-out + 高频回调 |
| scheduler tick 延迟 | 被 ingest 长事务阻塞，3s tick 可能变成 30s+ | 回调高峰期 |
| status poller 延迟 | mark_job 被 ingest 阻塞，job 状态更新慢 | 回调高峰期 |
| `database is locked` 错误 | 30s busy_timeout 耗尽后抛异常 | 极端并发 |

当前 890 天并发回补（5 并发）未触发问题，因为 downloader-dcp 本身有下载耗时，回调不会真正密集到达。但如果未来并发度提升或增加更多数据源，问题会暴露。

## 五、方案 A：应用层写队列

### 5.1 架构

将所有 SQLite 写操作序列化到一个专用写入线程，其他线程通过队列提交写请求。

```text
写请求线程（N个）              写入线程（1个）
  callback ingestion  ──┐
  fanout scheduler   ──┤──→ Queue ──→ 专用写入线程 ──→ SQLite
  status poller      ──┤
  plugin handler     ──┘
```

### 5.2 核心模型

```python
@dataclass
class WriteRequest:
    request_id: str
    fn: Callable[..., Any]
    args: tuple
    kwargs: dict
    result_event: threading.Event
    result: Any = None
    error: BaseException | None = None

class SQLiteWriteQueue:
    def __init__(self, store: DataHubStore):
        self._queue: queue.Queue[WriteRequest] = queue.Queue()
        self._shutdown = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="hub-sqlite-writer", daemon=True)
        self._thread.start()

    def submit(self, fn, *args, **kwargs) -> Any:
        """同步提交写请求，阻塞等待结果。"""
        req = WriteRequest(
            request_id=uuid4().hex[:8],
            fn=fn,
            args=args,
            kwargs=kwargs,
            result_event=threading.Event(),
        )
        self._queue.put(req)
        req.result_event.wait()  # 阻塞等待写入线程执行完毕
        if req.error is not None:
            raise req.error
        return req.result

    def submit_async(self, fn, *args, **kwargs) -> str:
        """异步提交写请求，不等待结果。返回 request_id。"""
        req = WriteRequest(
            request_id=uuid4().hex[:8],
            fn=fn,
            args=args,
            kwargs=kwargs,
            result_event=threading.Event(),
        )
        self._queue.put(req)
        return req.request_id

    def _loop(self):
        while not self._shutdown.is_set():
            try:
                req = self._queue.get(timeout=0.5)
                try:
                    req.result = req.fn(*req.args, **req.kwargs)
                except Exception as exc:
                    req.error = exc
                finally:
                    req.result_event.set()
            except queue.Empty:
                continue
```

### 5.3 改造方式

```python
# 改造前（直接写）
store.mark_job(job_id, status="running")

# 改造后（通过写队列）
write_queue.submit(store.mark_job, job_id, status="running")
```

对于长事务（如 `ingest_table_batch`），整个事务在写入线程中执行：

```python
# 改造后
result = write_queue.submit(ingestion_service.ingest_table_batch, payload.model_dump())
```

### 5.4 批量提交优化

写入线程可以攒批：从队列中取出多个请求，在一个事务中批量执行（适用于短写操作）。

```python
def _loop_with_batch(self):
    while not self._shutdown.is_set():
        batch = []
        try:
            req = self._queue.get(timeout=0.5)
            batch.append(req)
            # 非阻塞地取出更多请求
            while not self._queue.empty() and len(batch) < 50:
                batch.append(self._queue.get_nowait())
        except queue.Empty:
            continue

        # 短写操作可以合并到一个事务
        with closing(self.store.connect()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            for req in batch:
                try:
                    req.result = req.fn(*req.args, **req.kwargs, _conn=conn)
                except Exception as exc:
                    req.error = exc
            conn.commit()

        for req in batch:
            req.result_event.set()
```

### 5.5 优缺点

**优点：**
- 彻底消除写锁竞争，所有写操作串行执行，无需 busy_timeout
- 写入线程可以批量提交（batch commit），减少事务开销
- 其他线程不会阻塞在 SQLite 锁上
- 为未来迁移 PostgreSQL 提供了抽象层（替换写队列实现即可）

**缺点：**
- 需要改造所有写操作为"提交请求 + 等待结果"模式
- 复杂度较高，需要定义请求/响应协议
- 长事务（如 ingest_table_batch）在写入线程中执行时，其他写请求仍需等待
- 需要处理超时和错误传播

### 5.6 改动清单

| 改动 | 文件 | 说明 |
|---|---|---|
| 新增 WriteQueue 类 | `storage/write_queue.py` | 写队列核心实现 |
| 改造 store 写方法 | `storage/sqlite.py` | 所有写方法接受可选 `_conn` 参数 |
| 改造 ingest_table_batch | `ingestion/service.py` | 通过写队列提交 |
| 改造 fanout scheduler | `core/fanout_scheduler.py` | tick 写操作通过写队列提交 |
| 改造 status poller | `core/trigger_runtime.py` | mark_job 通过写队列提交 |
| 改造 plugin handler | `core/fan_out.py` | 写操作通过写队列提交 |
| 启动写队列 | `app.py` | 初始化 WriteQueue 并注入 |

## 六、方案 B：PRAGMA 优化 + BEGIN IMMEDIATE

不改变架构，只优化 SQLite 配置和事务模式。

### 6.1 具体改动

#### 6.1.1 PRAGMA synchronous = NORMAL

```python
# storage/sqlite.py connect()
def connect(self) -> sqlite3.Connection:
    self.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA synchronous = NORMAL")  # 新增
    return conn
```

WAL 模式下 `synchronous=NORMAL` 的安全性：
- 不会损坏数据库文件
- 断电时可能丢失最近几个事务（与 `synchronous=FULL` 的区别）
- 写性能提升显著（减少 fsync 次数）
- SQLite 官方文档推荐 WAL 模式使用 NORMAL

#### 6.1.2 BEGIN IMMEDIATE 替代 BEGIN

```python
# ingestion/service.py ingest_table_batch()
# 改造前
conn.execute("BEGIN")

# 改造后
conn.execute("BEGIN IMMEDIATE")
```

`BEGIN IMMEDIATE` 在事务开始时立即获取 RESERVED 锁，而不是等到第一个写操作时才获取。这消除了 deferred 事务的死锁风险：

```text
改造前（deferred）：
  事务 A: BEGIN → SELECT → INSERT (等锁) ← 可能死锁
  事务 B: BEGIN → SELECT → INSERT (等锁) ← 可能死锁

改造后（IMMEDIATE）：
  事务 A: BEGIN IMMEDIATE → 获取 RESERVED 锁 → 执行 → COMMIT
  事务 B: BEGIN IMMEDIATE → 等待 RESERVED 锁 → 获取 → 执行 → COMMIT
```

#### 6.1.3 限制 asyncio.to_thread 线程池

```python
# app.py 或 api/ingestion.py
import asyncio

# 创建受限线程池，替代默认的 ThreadPoolExecutor
write_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="hub-ingest")

# 在回调端点中使用
result = await asyncio.get_event_loop().run_in_executor(
    write_executor,
    ingestion_service.ingest_table_batch,
    payload.model_dump(),
)
```

限制并发写入者数量为 2，减少写锁排队。

#### 6.1.4 fanout scheduler tick 事务合并

当前一次 tick 对每个 running fanout_run 执行 10+ 次独立短连接写操作。可以合并为 2-3 个事务：

```text
事务 1（IMMEDIATE）：claim_run + reset_stale + sync_child_states + update_consecutive
事务 2（IMMEDIATE）：circuit_breaker_check + skip_pending + claim_and_submit_items
事务 3（IMMEDIATE）：close_parent_if_done
```

需要在 `storage/sqlite.py` 中新增接受外部 conn 参数的方法，或在 fanout_scheduler 中直接操作连接。

### 6.2 优缺点

**优点：**
- 改动最小，风险低
- `BEGIN IMMEDIATE` 消除 deferred 死锁风险
- `synchronous=NORMAL` 在 WAL 模式下写性能提升显著
- 不改变现有代码架构

**缺点：**
- 不解决根本问题，高并发下仍排队
- 线程池限制可能成为回调吞吐瓶颈
- fanout scheduler 事务合并需要改造 store 方法签名

### 6.3 改动清单

| 改动 | 文件 | 说明 |
|---|---|---|
| `PRAGMA synchronous = NORMAL` | `storage/sqlite.py` | connect() 中新增 |
| `BEGIN IMMEDIATE` | `ingestion/service.py` | 替代 `BEGIN` |
| 限制 to_thread 线程池 | `app.py` + `api/ingestion.py` | max_workers=2 |
| fanout scheduler tick 事务合并 | `fanout_scheduler.py` + `storage/sqlite.py` | 10+ 次短连接 → 2-3 次事务 |

## 七、推荐路径

**先做方案 B（低成本改进），观察效果；如果未来并发需求增长，再做方案 A。**

理由：

1. 当前 5 并发回补未触发问题，说明瓶颈尚未显现，方案 B 足以应对近期需求。
2. 方案 B 改动量小（4 处改动），可以在一次迭代中完成并验证。
3. 方案 A 是架构级改造，需要更充分的设计和测试，适合在并发需求明确增长时再实施。
4. 方案 B 中的 `BEGIN IMMEDIATE` 和 `synchronous=NORMAL` 在方案 A 中同样适用，不会浪费。

### 验证方法

方案 B 实施后，通过以下方式验证效果：

1. **基准测试**：5 并发回调写入，比较 P50/P99 延迟
2. **压力测试**：10 并发回调写入，观察是否出现 `database is locked`
3. **长事务测试**：单次 ingest 包含 5 个 table × 1000 rows，观察其他写入者的阻塞时间
4. **scheduler tick 延迟**：监控 tick 实际执行时间是否从 3s 漂移到 30s+

## 八、方案 C：迁移到 PostgreSQL（远期参考）

如果未来需要多进程部署、更高并发或更大数据量，迁移到 PostgreSQL 是根本解决方案。

**触发条件：**
- 单库数据量超过 10GB
- 需要多进程/多实例部署
- 写入 QPS 超过 100
- 需要更复杂的查询能力

**当前不应实施**，因为：
- MVP 阶段 SQLite 足够
- 增加部署复杂度
- 方案 A + B 可以覆盖中期需求
