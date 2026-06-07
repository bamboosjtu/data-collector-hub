# MVP Implementation Record

> Migrated from MVP_ARCHITECTURE.md on 2026-06-07.
> The architecture document now only retains long-term stable design decisions.
> Phase-specific implementation steps and acceptance records are kept here.

## 1. Refactoring Implementation Order (from Section 17)

Six phases:

### Phase 1: Core skeleton
- Schema registry + TableSpec + ColumnSpec
- validate_row / validate_scope
- Plugin loader (plugin.yaml + tables.yaml)

### Phase 2: Storage and schema
- SQLite DDL (metadata tables + business tables)
- Schema versioning
- init_schema with dev API keys

### Phase 3: TableBatch ingestion
- POST /ingestion/v1/table-batches endpoint
- Payload validation (dataset_key, tables, rows)
- Idempotency (message_id + idempotency_key + payload_hash)
- Writer (upsert / replace_scope / append)

### Phase 4: DCP plugin
- plugins/dcp/plugin.yaml (commands, connector, scope_mappings, query_routes)
- plugins/dcp/tables.yaml (12 business tables)
- Normalizers (plan_sgcc_year, plan_progress, dept_key_personnel, line_section)
- Fan-out handlers (refresh_towers_for_current_plan_projects, etc.)

### Phase 5: Trigger and scheduler
- ExternalSyncClient (downloader_sync trigger type)
- plugin_handler trigger type (fan_out.py)
- Job creation, status tracking, parent/child relationships

### Phase 6: Query and admin
- Dynamic query routes from plugin.yaml
- API key management (admin/ingestion/query scopes)
- Ops panel (/ops)
- CLI (src/datahub/cli.py)

## 2. Acceptance Criteria (from Section 18)

1. Core code contains zero DCP-specific logic
2. Plugin is pluggable — adding a new data source only requires a new plugin directory
3. Idempotency: duplicate message_id returns 200 + original result
4. Write modes (upsert/replace_scope/append) all have test coverage
5. query_routes are dynamically registered from plugin.yaml
6. API key scopes enforced on all protected endpoints
7. Schema registry validates unknown tables and unknown columns
8. Empty wrapper rows are skipped with logged reason; real business rows are never silently dropped
9. extra column only stores undeclared fields; raw/response/result/payload are filtered
10. plugin_handler loading validates plugin name prefix
11. Production mode requires explicit DATAHUB_CALLBACK_API_KEY
12. downloader-dcp is not modified by this project
13. All phase scripts pass

## 3. Tiered Acceptance Definition (from Section 20)

### Tier 1: Structural acceptance
- Hub starts without error
- All metadata tables exist
- All business tables exist with correct columns
- Schema version recorded

### Tier 2: Scheduling acceptance
- Command trigger creates ingestion_job
- downloader_sync type triggers external downloader
- plugin_handler type runs handler in background thread
- Parent/child job relationships work for fan-out
- Failed jobs can be retried

### Tier 3: Real data ingestion acceptance
- downloader-dcp callback returns 202
- Business tables have row_count > 0
- Skipped rows are recorded with reason
- Idempotent re-ingestion returns 200 + original result
- Query routes return DTO data (not raw DCP records)

### MVP acceptance record
See: docs/devlog/2026-06-06-dcp-plugin-mvp-validation.md
