# DataCollectorHub 持久化 Fan-out 并发改造方案

## 一、结论

推荐采用**持久化 fan-out 调度器**，而不是在线程池里阻塞等待 child job 终态。

目标模型：fan-out handler 只负责展开参数并写入 SQLite 调度状态；后台 scheduler tick 根据 SQLite 状态提交 child、同步终态、执行熔断并关闭 parent。SQLite 是唯一事实来源，进程重启后可以继续推进。

这比“ThreadPoolExecutor + `_wait_for_child_terminal()`”更稳健：

- 不长期占用 plugin handler 线程。
- 不依赖内存中的 `next_idx`、`results`、`consecutive_failures`。
- 崩溃重启后 pending/submitted child 可恢复。
- 熔断、skipped、parent summary 都可由数据库重建。
- 并发提交和 SQLite 单写约束都更可控。

## 二、当前问题

当前 fan-out 路径是严格串行：

```text
handler 后台线程
  for child_params in param_sets:
    _run_child_job()              # 同步 POST downloader
    _wait_for_child_terminal()    # 轮询 SQLite，最长 30min
    检查失败/熔断
    sleep(cooldown_seconds)
```

主要瓶颈和风险：

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | fan-out child 严格串行 | P0 | 416 项目约 30min，日期回补同样受限 |
| 2 | `_wait_for_child_terminal()` 阻塞线程 | High | 每个 child 最长占用 30min |
| 3 | 崩溃后 fan-out 内存上下文丢失 | High | parent 可能长期 running |
| 4 | 回调端点在 async 路由里同步写库 | High | 并发 callback 会阻塞事件循环 |
| 5 | SQLite `busy_timeout=5s` 偏短 | Medium | 并发写入更容易超时 |
| 6 | `CommandSpec` 没有并发字段 | Medium | `plugin.yaml` 新字段会被静默丢弃 |

## 三、目标架构

```text
POST /ingestion/v1/jobs fan-out command
  -> create parent ingestion_job
  -> plugin handler 展开 param_sets
  -> 写入 fanout_runs / fanout_items
  -> handler 立即返回

fanout_scheduler_tick 每 3s
  -> claim running fanout_run lease
  -> 恢复 stale submitting items
  -> 从 ingestion_jobs 同步 submitted child 终态
  -> 计算 stats 和连续失败
  -> 熔断则 skip pending，等待 submitted drain
  -> 未熔断则按 max_concurrency/cooldown claim pending item 并触发 child
  -> 全部终态后关闭 fanout_run 和 parent ingestion_job

poll_downloader_jobs 每 5s
  -> 同步 downloader child 状态到 ingestion_jobs
  -> 不再负责 fan-out parent 聚合，或跳过有 fanout_runs 的 parent
```

关键边界：

- scheduler 提交 child，但不直接轮询 downloader 状态。
- downloader 状态仍由现有 `poll_downloader_jobs()` 同步到 `ingestion_jobs`。
- scheduler 通过 `ingestion_jobs` 读取 child 终态并更新 `fanout_items`。
- fan-out parent 最终状态由 scheduler 写入，避免和 `_aggregate_parent_jobs()` 双写。

## 四、数据表

新增调度表应放进 `create_metadata_tables()`，与 `ingestion_jobs` 同一数据库。

```sql
CREATE TABLE IF NOT EXISTS fanout_runs (
  parent_job_id TEXT PRIMARY KEY,
  plugin_id TEXT NOT NULL,
  parent_command TEXT NOT NULL,
  child_command TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'running',
  total INTEGER NOT NULL,
  max_concurrency INTEGER NOT NULL DEFAULT 1,
  cooldown_seconds REAL NOT NULL DEFAULT 0,
  consecutive_failure_threshold INTEGER NOT NULL DEFAULT 5,
  consecutive_failures INTEGER NOT NULL DEFAULT 0,
  circuit_opened INTEGER NOT NULL DEFAULT 0,
  last_submit_at TEXT,
  result_json TEXT,
  lease_owner TEXT,
  lease_until TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fanout_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  parent_job_id TEXT NOT NULL,
  item_index INTEGER NOT NULL,
  params_json TEXT NOT NULL,
  child_job_id TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  error TEXT,
  claimed_by TEXT,
  claimed_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(parent_job_id, item_index),
  FOREIGN KEY(parent_job_id) REFERENCES fanout_runs(parent_job_id)
);

CREATE INDEX IF NOT EXISTS idx_fanout_runs_status_lease
  ON fanout_runs(status, lease_until);
CREATE INDEX IF NOT EXISTS idx_fanout_items_parent_status_index
  ON fanout_items(parent_job_id, status, item_index);
CREATE INDEX IF NOT EXISTS idx_fanout_items_child_job
  ON fanout_items(child_job_id);
```

### 状态机

`fanout_runs.status`:

- `running`: 正在调度或等待 submitted child 终态。
- `succeeded`: 全部已提交 child 成功，且没有 skipped/failed。
- `partial`: 有成功，也有 failed/skipped。
- `failed`: 没有成功，或熔断后整体失败。
- `cancelled`: 预留。

`fanout_items.status`:

- `pending`: 尚未提交。
- `submitting`: scheduler 已认领，正在调用 `_run_child_job()`。
- `submitted`: child job 已创建并提交给 downloader。
- `succeeded`: child 终态成功。
- `failed`: 触发失败或 child 终态失败。
- `skipped`: 熔断后未提交。

为什么需要 `submitting`：避免多个 scheduler tick 或多进程同时提交同一个 pending item；也能恢复“认领后进程崩溃但 child 尚未创建”的中间态。

## 五、Fan-out Handler

handler 不等待 child 终态，只创建调度状态。

注意现有 context key 是 `ingestion_job_id`，不是 `job_id`。

```python
def _project_fan_out(ctx: dict[str, Any], child_command: str, params_mapping: dict[str, str], *, cooldown_seconds: float = 3.0) -> dict[str, Any]:
    store = ctx["store"]
    parent_job_id = ctx["ingestion_job_id"]
    parent_command = ctx["command"].name
    plugin_id = ctx["plugin"].name
    params = ctx.get("params", {})

    param_sets = _build_project_param_sets(store, params_mapping, params)
    max_concurrency = _resolve_concurrency(ctx["command"], params)
    cooldown_seconds = _resolve_cooldown(ctx["command"], params, default=cooldown_seconds)
    threshold = _resolve_failure_threshold(params)

    store.create_fanout_run_with_items(
        parent_job_id=parent_job_id,
        plugin_id=plugin_id,
        parent_command=parent_command,
        child_command=child_command,
        param_sets=param_sets,
        max_concurrency=max_concurrency,
        cooldown_seconds=cooldown_seconds,
        consecutive_failure_threshold=threshold,
    )

    store.mark_job(
        parent_job_id,
        status="running",
        result={"fanout_scheduler": True, "total": len(param_sets), "max_concurrency": max_concurrency},
    )
    return {"status": "running", "total": len(param_sets), "max_concurrency": max_concurrency}
```

Implementation notes:

- Use one transaction for `fanout_runs` + all `fanout_items`, so a parent is never half-initialized.
- If `param_sets` is empty, close the parent as `succeeded` immediately and do not create a running fanout_run.
- Clean fan-out control params before storing child params, same as current code removes `max_items/max_concurrency/cooldown_seconds/consecutive_failure_threshold`.
- Keep the old serial path behind an explicit flag only if rollback requires it; default path should be scheduler-backed.

## 六、Scheduler Tick

### Startup

Scheduler needs runtime context that is not stored in DB:

- `store`
- `plugins`
- `trigger_clients`
- `callback_base_url`
- `callback_headers`
- a unique `scheduler_id`

Do not persist callback API keys in `fanout_runs`; pass them from app settings when starting the scheduler.

```python
def start_fanout_scheduler(store, trigger_clients, plugins, *, callback_base_url: str, callback_headers: dict[str, str] | None, tick_interval: float = 3.0):
    scheduler_id = f"hub-{os.getpid()}-{uuid4().hex[:8]}"
    shutdown = threading.Event()

    def loop():
        while not shutdown.is_set():
            fanout_scheduler_tick(
                store,
                trigger_clients,
                plugins,
                callback_base_url=callback_base_url,
                callback_headers=callback_headers,
                scheduler_id=scheduler_id,
            )
            shutdown.wait(tick_interval)

    thread = threading.Thread(target=loop, name="hub-fanout-scheduler", daemon=True)
    thread.start()
    return shutdown
```

### Claim Run Lease

Even if local MVP usually runs one process, make the scheduler safe for duplicate starts. Each tick should claim a run lease before advancing it.

```sql
UPDATE fanout_runs
SET lease_owner = ?, lease_until = ?, updated_at = ?
WHERE parent_job_id = ?
  AND status = 'running'
  AND (lease_until IS NULL OR lease_until < ? OR lease_owner = ?)
```

If affected rows is `0`, another scheduler owns the run and this tick skips it.

### Advance Run

```python
def _advance_fanout_run(store, trigger_clients, plugins, run, *, callback_base_url, callback_headers, scheduler_id):
    parent_job_id = run["parent_job_id"]

    if not store.claim_fanout_run(parent_job_id, scheduler_id, lease_seconds=30):
        return

    now = datahub_now_text()

    # 1. Recover stale submitting items. These were claimed but never became child jobs.
    store.reset_stale_submitting_items(parent_job_id, stale_seconds=120)

    # 2. Sync submitted child terminal states from ingestion_jobs into fanout_items.
    for item in store.list_submitted_fanout_items(parent_job_id):
        child_job = store.get_job(item["child_job_id"])
        if child_job and child_job["status"] in _TERMINAL_STATUSES:
            failed = _is_child_failed(child_job)
            store.update_fanout_item_terminal(
                item["id"],
                status="failed" if failed else "succeeded",
                error=child_job.get("error") if failed else None,
            )

    stats = store.get_fanout_stats(parent_job_id)
    consecutive_failures = store.get_consecutive_failures(parent_job_id)
    store.update_fanout_run_consecutive(parent_job_id, consecutive_failures)

    # 3. If circuit is open, stop creating new children but keep draining submitted items.
    if not run["circuit_opened"] and consecutive_failures >= run["consecutive_failure_threshold"]:
        store.mark_fanout_circuit_open(parent_job_id)
        store.skip_pending_fanout_items(parent_job_id)
        stats = store.get_fanout_stats(parent_job_id)

    # 4. Close only when no pending/submitting/submitted work remains.
    if stats["pending"] == 0 and stats["submitting"] == 0 and stats["submitted"] == 0:
        _close_fanout_parent(store, parent_job_id)
        return

    # 5. If circuit is open, do not submit more; wait for submitted items to drain.
    run = store.get_fanout_run(parent_job_id)
    if run["circuit_opened"]:
        return

    # 6. Submit new work within capacity and cooldown.
    capacity = run["max_concurrency"] - stats["submitted"] - stats["submitting"]
    while capacity > 0:
        if not _cooldown_elapsed(run["last_submit_at"], run["cooldown_seconds"]):
            break

        item = store.claim_next_pending_fanout_item(parent_job_id, scheduler_id)
        if item is None:
            break

        _submit_claimed_item(
            store,
            trigger_clients,
            plugins,
            run,
            item,
            callback_base_url=callback_base_url,
            callback_headers=callback_headers,
        )
        store.update_fanout_run_submit(parent_job_id, datahub_now_text())
        run = store.get_fanout_run(parent_job_id)
        capacity -= 1
```

### Submit Claimed Item

Use the real existing command/plugin contract:

- `find_command(plugins, child_command)` returns `CommandSpec`.
- `find_plugin_for_job(plugins, child_command)` returns `PluginSpec`.
- downloader job type comes from `child_cmd.trigger["job_type"]`.
- connector client comes from `trigger_clients[child_plugin.name]`.
- `_run_child_job()` returns `(child_job_id, status, err)`.

```python
def _submit_claimed_item(store, trigger_clients, plugins, run, item, *, callback_base_url, callback_headers):
    child_command = run["child_command"]
    child_cmd = find_command(plugins, child_command)
    child_plugin = find_plugin_for_job(plugins, child_command)
    if child_cmd is None or child_plugin is None:
        store.update_fanout_item_terminal(item["id"], status="failed", error=f"child command not found: {child_command}")
        return

    client = trigger_clients.get(child_plugin.name)
    downloader_job_type = child_cmd.trigger.get("job_type")
    if client is None or not downloader_job_type:
        store.update_fanout_item_terminal(item["id"], status="failed", error=f"child connector/job_type missing: {child_command}")
        return

    params = json.loads(item["params_json"])
    child_job_id, child_status, err = _run_child_job(
        store,
        child_plugin,
        client,
        downloader_job_type,
        child_command,
        params,
        run["parent_job_id"],
        callback_base_url,
        callback_headers=callback_headers,
    )

    if err:
        store.update_fanout_item_terminal(item["id"], status="failed", child_job_id=child_job_id, error=err)
    else:
        store.update_fanout_item_submitted(item["id"], child_job_id=child_job_id)
```

## 七、Atomic Store APIs

The store methods must be transaction-aware. Important operations should be atomic, especially item claiming.

Required methods:

```python
create_fanout_run_with_items(...)
get_running_fanout_runs(limit=50)
claim_fanout_run(parent_job_id, scheduler_id, lease_seconds)
get_fanout_run(parent_job_id)
list_submitted_fanout_items(parent_job_id)
reset_stale_submitting_items(parent_job_id, stale_seconds)
claim_next_pending_fanout_item(parent_job_id, scheduler_id)
update_fanout_item_submitted(item_id, child_job_id)
update_fanout_item_terminal(item_id, status, child_job_id=None, error=None)
skip_pending_fanout_items(parent_job_id)
get_fanout_stats(parent_job_id)
get_consecutive_failures(parent_job_id)
update_fanout_run_consecutive(parent_job_id, count)
mark_fanout_circuit_open(parent_job_id)
update_fanout_run_submit(parent_job_id, last_submit_at)
close_fanout_run(parent_job_id, status, result)
```

`claim_next_pending_fanout_item()` should be an atomic update-then-select. SQLite supports this with a transaction:

```sql
BEGIN IMMEDIATE;
SELECT id FROM fanout_items
WHERE parent_job_id = ? AND status = 'pending'
ORDER BY item_index
LIMIT 1;
UPDATE fanout_items
SET status = 'submitting', claimed_by = ?, claimed_at = ?, updated_at = ?
WHERE id = ? AND status = 'pending';
COMMIT;
```

If the update affects zero rows, another scheduler claimed it; return `None`.

## 八、连续失败与熔断

连续失败 should be derived from persisted item state, not trusted from memory.

```python
def get_consecutive_failures(parent_job_id: str) -> int:
    rows = conn.execute(
        """
        SELECT status FROM fanout_items
        WHERE parent_job_id = ? AND status IN ('succeeded', 'failed')
        ORDER BY item_index DESC
        """,
        (parent_job_id,),
    ).fetchall()
    count = 0
    for row in rows:
        if row["status"] == "failed":
            count += 1
        else:
            break
    return count
```

Important semantics:

- Submitted work is allowed to finish after circuit opens.
- Pending work is marked `skipped` when circuit opens.
- Parent is closed only after `submitted/submitting` reaches zero.
- Because concurrency hides ordering, up to `max_concurrency - 1` extra child jobs may already be submitted before circuit opens. This is acceptable and should be visible in result summary.

## 九、Parent Close Semantics

Scheduler owns fan-out parent completion. Existing `_aggregate_parent_jobs()` should skip parent jobs that have a row in `fanout_runs`, otherwise scheduler and poller may race to write parent status.

Recommended final parent mapping:

```python
if succeeded > 0 and failed == 0 and skipped == 0:
    parent_status = "succeeded"
elif succeeded > 0:
    parent_status = "partial"
else:
    parent_status = "failed"
```

`fanout_runs.status` can mirror this final status. Include circuit metadata in result:

```json
{
  "total": 416,
  "succeeded": 390,
  "failed": 5,
  "skipped": 21,
  "submitted": 395,
  "circuit_opened": true,
  "consecutive_failure_threshold": 5,
  "max_concurrency": 5
}
```

Call `store.mark_job(parent_job_id, status=parent_status, result=result, error=error_msg)` with a dict result. Do not pre-serialize `result_json` before passing to `mark_job()`, because `mark_job()` already serializes dicts.

## 十、CommandSpec 并发配置

Current `CommandSpec` and `_parse_command()` must be extended before adding YAML fields.

```python
@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str = ""
    required_params: tuple[str, ...] = ()
    trigger: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    max_concurrency: int = 1
    max_concurrency_limit: int | None = None
    cooldown_seconds: float = 0.0
```

```python
def _parse_command(item: dict[str, Any]) -> CommandSpec:
    mc = max(1, int(item.get("max_concurrency", 1)))
    raw_limit = item.get("max_concurrency_limit")
    limit = max(mc, int(raw_limit)) if raw_limit is not None else None
    cooldown = max(0.0, float(item.get("cooldown_seconds", 0.0)))
    return CommandSpec(
        name=str(item.get("name") or item.get("job_type", "")),
        description=str(item.get("description", "")),
        required_params=tuple(item.get("required_params") or ()),
        trigger=dict(item.get("trigger") or {}),
        enabled=bool(item.get("enabled", True)),
        max_concurrency=mc,
        max_concurrency_limit=limit,
        cooldown_seconds=cooldown,
    )
```

Resolution rule:

```python
def _resolve_concurrency(command_spec, params):
    default = command_spec.max_concurrency
    limit = command_spec.max_concurrency_limit or default
    requested = int(params.get("max_concurrency", default))
    return max(1, min(requested, limit))
```

`max_concurrency_limit` is manual configuration. Hub currently has no automatic downloader capacity discovery.

## 十一、Callback Endpoint

Keep the existing async route and JSON validation, but move the synchronous DB write to a worker thread.

```python
result = await asyncio.to_thread(
    ingestion_service.ingest_table_batch,
    payload.model_dump(),
)
```

Keep the current HTTP status mapping unchanged:

- `conflict` -> 409
- ordinary `failed` -> 422
- `storage_error` -> 500

## 十二、SQLite Settings

Change only hot-path timeout:

```python
def connect(self) -> sqlite3.Connection:
    self.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn
```

Keep `PRAGMA journal_mode = WAL` in `init_schema()` only. WAL is a database-level persistent mode and does not need to be set on every connection.

## 十三、Crash Recovery

Recovery behavior:

| State | Recovery |
|-------|----------|
| `pending` | scheduler can claim and submit later |
| `submitting` with stale `claimed_at` and no `child_job_id` | reset to `pending` |
| `submitted` | poller continues syncing downloader status; scheduler later marks succeeded/failed |
| `circuit_opened=1` with submitted items | scheduler drains submitted items, no new submissions |
| run lease expired | another scheduler can claim and continue |

No special bootstrap recovery routine is required beyond scheduler tick recovery steps.

## 十四、Implementation Order

| Step | Change | Files | Verification |
|------|--------|-------|--------------|
| 1 | `asyncio.to_thread` callback write + `busy_timeout=30000` | `api/ingestion.py`, `storage/sqlite.py` | concurrent callback/ingest tests |
| 2 | extend `CommandSpec` and parser | `core/specs.py`, `core/plugin_loader.py` | parser tests |
| 3 | add fanout tables and store CRUD/claim APIs | `storage/ddl.py`, `storage/sqlite.py` | CRUD + atomic claim tests |
| 4 | convert fan-out handlers to create runs/items | `plugins/dcp/fan_out.py` | handler returns quickly; rows created |
| 5 | add scheduler tick and run lease | `core/fanout_scheduler.py` | unit tests for submit/cooldown/circuit/recovery |
| 6 | integrate scheduler startup/shutdown | `app.py` | smoke test with local downloader |
| 7 | update `_aggregate_parent_jobs()` to skip `fanout_runs` parents | `core/trigger_runtime.py` | no parent double-write |
| 8 | add `plugin.yaml` concurrency config | `plugins/dcp/plugin.yaml` | capped user override tests |
| 9 | full fan-out regression | end-to-end | 416 project run, date backfill, restart recovery |

## 十五、不改动

- `ExternalSyncClient` remains synchronous in phase 1.
- downloader-dcp is unchanged.
- `poll_downloader_jobs()` remains the downloader status source of truth.
- No global `threading.Lock`; use SQLite short transactions and atomic claims.
- `_wait_for_child_terminal()` can remain for compatibility, but fan-out paths should no longer call it.
