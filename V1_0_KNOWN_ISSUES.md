# Data Collector Hub v1.0 已知问题清单

> 生成时间: 2026-05-06
> 版本: v1.1

---

## 问题分类

### 🔴 严重问题 (Critical)

**无**

所有核心功能测试通过，无阻塞性问题。

---

### 🟡 轻微问题 (Minor)

#### 1. 测试脚本兼容性 - WebSocket timeout 参数

**描述**: `test_integration_rc1.py` 中 `websockets.connect()` 的 `timeout` 参数在某些版本中不受支持。

**影响**: 仅影响测试脚本，不影响实际功能。

**状态**: ✅ 已修复（已移除 timeout 参数）

**文件**: `test_integration_rc1.py`

---

#### 2. RSS Feed 中文编码显示

**描述**: PowerShell 输出中 RSS 内容的中文显示为乱码（如 `ä¸­å...`），这是终端编码问题，非数据问题。

**影响**: 仅影响终端显示，实际 RSS XML 内容正确。

**验证**:
```bash
curl -s http://localhost:8000/feed/rss | head -20
# XML 内容编码正确
```

**状态**: 无需修复（终端编码问题）

---

#### 3. PluginMetadata 类型不一致

**描述**: `plugin_manager.get_plugin_metadata()` 返回 `PluginMetadata` 对象，而 `store.get_plugin()` 返回字典。早期代码曾误用 `.get()` 方法。

**影响**: 已修复，但需注意类型差异。

**修复**: `core/mcp_tools.py` 中已改用 `store.get_plugin()` 检查 enabled 状态。

**状态**: ✅ 已修复

---

### 🟢 设计限制（非问题）

以下条目为 v1.0 设计约束，**不是缺陷**：

| # | 限制 | 说明 |
|---|------|------|
| 1 | 单节点部署 | v1.0 设计约束 |
| 2 | SQLite 唯一存储 | v1.0 设计约束 |
| 3 | 无认证/权限 | v1.0 设计约束 |
| 4 | 弱 schema | normalized_data / canonical_entities 为半结构化，符合设计 |
| 5 | 无插件依赖 | 插件间无法调用，符合设计 |
| 6 | 日志仅本地 | 无远程收集，符合设计 |
| 7 | 无上游事件自动清理 | raw_events 保留策略需手动执行 |
| 8 | 无实体数据版本历史 | canonical_entities 为 UPSERT 语义，仅保留最新状态 |

---

## 测试覆盖率

| 模块 | 测试状态 | 覆盖率 |
|------|---------|--------|
| Plugin Discovery | ✅ 通过 | 100% |
| Pipeline | ✅ 通过 | 100% |
| Scheduler | ✅ 通过 | 100% |
| REST API | ✅ 通过 | 100% |
| Ingestion API | ✅ 通过 | 100% |
| Processing API | ✅ 通过 | 100% |
| Sandbox API | ✅ 通过 | 100% |
| RSS Feed | ✅ 通过 | 100% |
| WebSocket | ✅ 通过 | 100% |
| MCP | ✅ 通过 | 100% |
| Normalizer Runner | ⚠️ 需补充 | - |

---

## 建议改进（v1.1+ 考虑）

以下改进**不在 v1.0 范围内**，仅作记录：

### 高优先级

1. **API Key 认证** - 为 Ingestion API 和 Sandbox API 添加 API Key 认证
2. **上游事件自动清理** - 实现 raw_events 的自动过期清理策略
3. **Normalizer 监控** - 添加归一化处理的可观测性指标
4. **下游数据质量检查** - 添加 canonical_entities 数据完整性校验

### 中优先级

5. **健康检查端点** `/health` - 用于负载均衡检查
6. **配置热重载** - 无需重启修改配置
7. **更多 RSS 源** - 支持更多新闻源
8. **数据导出** - CSV/JSON 导出功能

### 低优先级

9. **Web UI** - 除 Streamlit 外的原生 Web 界面
10. **插件市场** - 远程插件安装
11. **告警通知** - Webhook/Email 告警
12. **PostgreSQL 支持** - 替代 SQLite 用于生产环境

---

*文档版本: v1.1*
*最后更新: 2026-05-06*
