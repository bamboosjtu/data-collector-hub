from __future__ import annotations

import json
from typing import Any

COMMON_ENTITY_COLUMNS: tuple[tuple[str, str], ...] = (
    ("entity_key", "TEXT NOT NULL UNIQUE"),
    ("entity_date", "TEXT"),
    ("dataset_key", "TEXT NOT NULL"),
    ("source_system", "TEXT NOT NULL"),
    ("source_record_key", "TEXT NOT NULL"),
    ("latest_raw_event_id", "INTEGER NOT NULL"),
    ("latest_collected_at", "TIMESTAMP"),
    ("latest_collected_at_epoch", "REAL"),
    ("latest_source_record_hash", "TEXT"),
    ("source_refs", "TEXT NOT NULL DEFAULT '[]'"),
    ("extra_attributes_json", "TEXT"),
    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
)

ENTITY_SPECS: dict[str, dict[str, Any]] = {
    "project": {
        "table": "canonical_projects",
        "columns": (
            ("project_code", "TEXT"),
            ("project_name", "TEXT"),
        ),
    },
    "single_project": {
        "table": "canonical_single_projects",
        "columns": (
            ("project_code", "TEXT"),
            ("single_project_code", "TEXT"),
            ("bidding_section_code", "TEXT"),
            ("project_status", "TEXT"),
            ("single_project_name", "TEXT"),
        ),
    },
    "bidding_section": {
        "table": "canonical_bid_sections",
        "columns": (
            ("project_code", "TEXT"),
            ("single_project_code", "TEXT"),
            ("bidding_section_code", "TEXT"),
            ("bidding_section_name", "TEXT"),
        ),
    },
    "project_progress": {
        "table": "canonical_project_progress",
        "columns": (
            ("project_code", "TEXT"),
            ("project_name", "TEXT"),
            ("progress_status", "TEXT"),
            ("raw_json", "TEXT"),
        ),
    },
    "line_section": {
        "table": "canonical_line_sections",
        "columns": (
            ("project_code", "TEXT"),
            ("project_name", "TEXT"),
            ("single_project_code", "TEXT"),
            ("single_project_name", "TEXT"),
            ("bidding_section_code", "TEXT"),
            ("bidding_section_name", "TEXT"),
            ("line_section_id", "TEXT"),
            ("line_section_name", "TEXT"),
            ("known_issues_json", "TEXT"),
            ("raw_json", "TEXT"),
        ),
    },
    "tower": {
        "table": "canonical_towers",
        "columns": (
            ("tower_id", "TEXT"),
            ("dcp_tower_id", "TEXT"),
            ("dcp_entity_key_fallback", "INTEGER"),
            ("project_code", "TEXT"),
            ("single_project_code", "TEXT"),
            ("bidding_section_code", "TEXT"),
            ("tower_no", "TEXT"),
            ("upstream_tower_no", "TEXT"),
            ("longitude", "REAL"),
            ("latitude", "REAL"),
            ("tower_type", "TEXT"),
            ("tower_full_height", "REAL"),
            ("nominal_height", "REAL"),
            ("known_issues_json", "TEXT"),
            ("raw_json", "TEXT"),
        ),
    },
    "station": {
        "table": "canonical_stations",
        "columns": (
            ("project_code", "TEXT"),
            ("single_project_code", "TEXT"),
            ("bidding_section_code", "TEXT"),
            ("dcp_coordinate_id", "TEXT"),
            ("longitude", "REAL"),
            ("latitude", "REAL"),
            ("raw_json", "TEXT"),
        ),
    },
    "work_point": {
        "table": "canonical_work_points",
        "columns": (
            ("project_code", "TEXT"),
            ("single_project_code", "TEXT"),
            ("bidding_section_code", "TEXT"),
            ("project_name", "TEXT"),
            ("longitude", "REAL"),
            ("latitude", "REAL"),
            ("person_count", "INTEGER"),
            ("risk_level", "TEXT"),
            ("work_status", "TEXT"),
            ("voltage_level", "TEXT"),
            ("city", "TEXT"),
            ("work_date", "TEXT"),
            ("coordinate_in_hunan", "INTEGER"),
            ("source_file_work_date", "TEXT"),
            ("raw_current_constr_date", "TEXT"),
            ("raw_work_start_time", "TEXT"),
            ("raw_json", "TEXT"),
        ),
    },
}

JSON_ATTRIBUTE_COLUMNS = {"raw_json": "raw", "known_issues_json": "known_issues"}
BOOL_ATTRIBUTE_COLUMNS = {"coordinate_in_hunan"}


def canonical_schema_sql() -> str:
    statements: list[str] = []
    for entity_type, spec in ENTITY_SPECS.items():
        column_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        column_defs.extend(f"{name} {sql_type}" for name, sql_type in COMMON_ENTITY_COLUMNS)
        column_defs.extend(f"{name} {sql_type}" for name, sql_type in spec["columns"])
        statements.append(
            f"""
CREATE TABLE IF NOT EXISTS {spec['table']} (
    {",\n    ".join(column_defs)}
);
"""
        )
        statements.append(
            f"CREATE INDEX IF NOT EXISTS idx_{spec['table']}_dataset ON {spec['table']}(dataset_key);"
        )
        statements.append(
            f"CREATE INDEX IF NOT EXISTS idx_{spec['table']}_updated ON {spec['table']}(updated_at DESC, id DESC);"
        )
        statements.append(
            f"CREATE INDEX IF NOT EXISTS idx_{spec['table']}_entity_date ON {spec['table']}(entity_date);"
        )
        for column_name, _sql_type in spec["columns"]:
            if column_name.endswith("_code") or column_name in {
                "project_name",
                "line_section_id",
                "line_section_name",
                "tower_no",
                "work_date",
            }:
                statements.append(
                    f"CREATE INDEX IF NOT EXISTS idx_{spec['table']}_{column_name} ON {spec['table']}({column_name});"
                )
        statements.append(
            f"CREATE VIEW IF NOT EXISTS canonical_{entity_type}_view AS SELECT * FROM {spec['table']};"
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


def entity_spec(entity_type: str) -> dict[str, Any]:
    if entity_type not in ENTITY_SPECS:
        raise KeyError(f"unsupported canonical entity_type: {entity_type}")
    return ENTITY_SPECS[entity_type]


def encode_entity_columns(entity_type: str, attributes: dict[str, Any]) -> dict[str, Any]:
    spec = entity_spec(entity_type)
    encoded: dict[str, Any] = {}
    handled_attributes: set[str] = set()
    for column_name, _sql_type in spec["columns"]:
        attribute_name = JSON_ATTRIBUTE_COLUMNS.get(column_name, column_name)
        handled_attributes.add(attribute_name)
        value = attributes.get(attribute_name)
        if column_name in JSON_ATTRIBUTE_COLUMNS:
            encoded[column_name] = (
                json.dumps(value, ensure_ascii=False, default=str)
                if value is not None
                else None
            )
        elif column_name in BOOL_ATTRIBUTE_COLUMNS:
            encoded[column_name] = None if value is None else (1 if bool(value) else 0)
        else:
            encoded[column_name] = value
    extra_attributes = {
        key: value
        for key, value in attributes.items()
        if key not in handled_attributes
    }
    encoded["extra_attributes_json"] = (
        json.dumps(extra_attributes, ensure_ascii=False, default=str)
        if extra_attributes
        else None
    )
    return encoded


def decode_entity_attributes(entity_type: str, row: dict[str, Any]) -> dict[str, Any]:
    spec = entity_spec(entity_type)
    attributes: dict[str, Any] = {}
    extra_attributes_json = row.get("extra_attributes_json")
    if extra_attributes_json not in (None, ""):
        attributes.update(json.loads(extra_attributes_json))
    for column_name, _sql_type in spec["columns"]:
        value = row.get(column_name)
        if column_name in JSON_ATTRIBUTE_COLUMNS:
            decoded = None if value in (None, "") else json.loads(value)
            if decoded is not None:
                attributes[JSON_ATTRIBUTE_COLUMNS[column_name]] = decoded
        elif column_name in BOOL_ATTRIBUTE_COLUMNS:
            attributes[column_name] = None if value is None else bool(value)
        else:
            attributes[column_name] = value
    return attributes


def all_entity_types() -> list[str]:
    return list(ENTITY_SPECS.keys())
