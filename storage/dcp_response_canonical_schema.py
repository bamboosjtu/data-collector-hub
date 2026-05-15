from __future__ import annotations

from typing import Any

from plugins.dcp_response_registry import DCP_RESPONSE_TABLES


COMMON_RESPONSE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("entity_key", "TEXT NOT NULL UNIQUE"),
    ("key_quality", "TEXT NOT NULL"),
    ("dataset_key", "TEXT NOT NULL"),
    ("plugin_id", "TEXT NOT NULL"),
    ("page_name", "TEXT NOT NULL"),
    ("api_name", "TEXT NOT NULL"),
    ("record_path", "TEXT NOT NULL"),
    ("partition_key", "TEXT"),
    ("partition_value", "TEXT"),
    ("source_system", "TEXT NOT NULL"),
    ("source_record_key", "TEXT NOT NULL"),
    ("latest_raw_event_id", "INTEGER NOT NULL"),
    ("latest_collected_at", "TIMESTAMP"),
    ("latest_collected_at_epoch", "REAL"),
    ("latest_source_record_hash", "TEXT"),
    ("source_refs", "TEXT NOT NULL DEFAULT '[]'"),
    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
)


def response_canonical_schema_sql() -> str:
    statements: list[str] = []
    for entry in DCP_RESPONSE_TABLES:
        table = entry["table"]
        column_defs = ["row_id INTEGER PRIMARY KEY AUTOINCREMENT"]
        column_defs.extend(f"{name} {sql_type}" for name, sql_type in COMMON_RESPONSE_COLUMNS)
        column_defs.extend(
            f"{column['name']} {column['type']}" for column in entry.get("columns", [])
        )
        statements.append(
            f"""
CREATE TABLE IF NOT EXISTS {table} (
    {",\n    ".join(column_defs)}
);
"""
        )
        statements.extend(
            [
                f"CREATE INDEX IF NOT EXISTS idx_{table}_dataset ON {table}(dataset_key);",
                f"CREATE INDEX IF NOT EXISTS idx_{table}_plugin ON {table}(plugin_id);",
                f"CREATE INDEX IF NOT EXISTS idx_{table}_api ON {table}(api_name);",
                f"CREATE INDEX IF NOT EXISTS idx_{table}_partition ON {table}(partition_key, partition_value);",
                f"CREATE INDEX IF NOT EXISTS idx_{table}_updated ON {table}(updated_at DESC, row_id DESC);",
            ]
        )
    statements.append(
        """
CREATE TABLE IF NOT EXISTS canonical_entity_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    dataset_key TEXT NOT NULL,
    source_system TEXT NOT NULL,
    raw_event_id INTEGER NOT NULL,
    request_id TEXT,
    batch_id TEXT,
    source_record_key TEXT NOT NULL,
    source_record_hash TEXT,
    collected_at TIMESTAMP,
    collected_at_epoch REAL,
    attributes_snapshot TEXT NOT NULL,
    source_refs TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
    )
    statements.append(
        "CREATE INDEX IF NOT EXISTS idx_canonical_entity_observations_identity ON canonical_entity_observations(entity_type, entity_key, collected_at DESC, id DESC);"
    )
    statements.append(
        "CREATE INDEX IF NOT EXISTS idx_canonical_entity_observations_dataset ON canonical_entity_observations(dataset_key);"
    )
    return "\n".join(statements)


def response_table_by_name(table_name: str) -> dict[str, Any]:
    for entry in DCP_RESPONSE_TABLES:
        if entry["table"] == table_name:
            return entry
    raise KeyError(f"unsupported response canonical table: {table_name}")


def response_tables_for_dataset(dataset_key: str) -> list[dict[str, Any]]:
    return [entry for entry in DCP_RESPONSE_TABLES if entry["dataset_key"] == dataset_key]
