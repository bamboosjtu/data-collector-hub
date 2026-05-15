from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import PurePath
from typing import Any

from plugins.dcp_response_registry import table_for_record, tables_for_api


RESPONSE_CANONICAL_VERSION = "response_canonical.v1"


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _parse_epoch(value: Any) -> float | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def _json_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return value


def _source_file_date(raw_event: dict[str, Any]) -> str | None:
    source_file = raw_event.get("source_file")
    if not source_file:
        source_ref = raw_event.get("source_ref")
        if isinstance(source_ref, dict):
            source_file = source_ref.get("source_file")
    if not source_file:
        return None
    stem = PurePath(str(source_file).replace("\\", "/")).stem
    if len(stem) == 10 and stem[4] == "-" and stem[7] == "-":
        return stem
    return None


def _record_key(
    *,
    raw_event: dict[str, Any],
    record: dict[str, Any],
    record_path: str,
    entry: dict[str, Any],
) -> tuple[str, str]:
    for candidate in entry.get("key_candidates") or []:
        if candidate == "source_record_key+record_path":
            continue
        if "+" in candidate:
            values = [record.get(part) for part in candidate.split("+")]
            if all(value not in (None, "") for value in values):
                return "|".join(str(value) for value in values), "business_composite"
        else:
            value = record.get(candidate)
            if value not in (None, ""):
                return str(value), candidate
    fallback = ":".join(
        [
            str(raw_event.get("source_record_key") or raw_event.get("raw_event_key") or raw_event.get("id")),
            record_path,
            _json_hash(record),
        ]
    )
    return fallback, "source_path_fallback"


def _partition_value(raw_event: dict[str, Any], record: dict[str, Any], entry: dict[str, Any]) -> Any:
    field = entry.get("partition_field")
    if field:
        return record.get(field)
    if entry.get("partition_key") == "source_file_date":
        return _source_file_date(raw_event)
    return None


def _source_ref(raw_event: dict[str, Any], *, record_path: str, entity_key: str) -> dict[str, Any]:
    return {
        "source_system": raw_event.get("source_system"),
        "dataset_key": raw_event.get("dataset_key"),
        "plugin_id": raw_event.get("plugin_id"),
        "request_id": raw_event.get("request_id"),
        "batch_id": raw_event.get("batch_id"),
        "source_record_key": raw_event.get("source_record_key"),
        "source_record_id": raw_event.get("source_record_id"),
        "source_record_hash": raw_event.get("source_record_hash"),
        "raw_event_id": raw_event.get("id"),
        "record_path": record_path,
        "entity_key": entity_key,
    }


def _row_payload(
    *,
    raw_event: dict[str, Any],
    record: dict[str, Any],
    record_path: str,
    entry: dict[str, Any],
) -> dict[str, Any]:
    key_value, key_quality = _record_key(
        raw_event=raw_event,
        record=record,
        record_path=record_path,
        entry=entry,
    )
    entity_key = ":".join(
        [
            str(entry["plugin_id"]),
            str(entry["api_name"]),
            str(entry["record_path"]),
            key_value,
        ]
    )
    source_refs = [_source_ref(raw_event, record_path=record_path, entity_key=entity_key)]
    column_values: dict[str, Any] = {}
    for column in entry.get("columns") or []:
        column_values[column["name"]] = _json_value(record.get(column["source"]))
    collected_at = raw_event.get("collected_at")
    return {
        "table": entry["table"],
        "entity_key": entity_key,
        "key_quality": key_quality,
        "dataset_key": entry["dataset_key"],
        "plugin_id": entry["plugin_id"],
        "page_name": entry["page_name"],
        "api_name": entry["api_name"],
        "record_path": record_path,
        "partition_key": entry.get("partition_key"),
        "partition_value": _partition_value(raw_event, record, entry),
        "source_system": raw_event.get("source_system") or "dcp",
        "source_record_key": raw_event.get("source_record_key") or entity_key,
        "latest_raw_event_id": int(raw_event.get("id") or 0),
        "latest_collected_at": collected_at,
        "latest_collected_at_epoch": _parse_epoch(collected_at),
        "latest_source_record_hash": raw_event.get("source_record_hash"),
        "source_refs": source_refs,
        "columns": column_values,
        "snapshot": {
            "governance": {
                "entity_key": entity_key,
                "key_quality": key_quality,
                "dataset_key": entry["dataset_key"],
                "plugin_id": entry["plugin_id"],
                "page_name": entry["page_name"],
                "api_name": entry["api_name"],
                "record_path": record_path,
            },
            "record": record,
        },
        "request_id": raw_event.get("request_id"),
        "batch_id": raw_event.get("batch_id"),
    }


def _child_records(record: dict[str, Any], record_path: str) -> list[tuple[str, dict[str, Any]]]:
    children: list[tuple[str, dict[str, Any]]] = []
    for key, value in record.items():
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                children.append((f"{record_path}.{key}[]", item))
    return children


def _relationship(parent: dict[str, Any], child: dict[str, Any], raw_event: dict[str, Any]) -> dict[str, Any]:
    relationship_type = "HAS_RESPONSE_CHILD"
    return {
        "relationship_key": ":".join(
            [
                "dcp-response",
                relationship_type,
                parent["entity_key"],
                child["entity_key"],
            ]
        ),
        "relationship_type": relationship_type,
        "from_entity_type": parent["record_path"],
        "from_entity_key": parent["entity_key"],
        "to_entity_type": child["record_path"],
        "to_entity_key": child["entity_key"],
        "dataset_key": child["dataset_key"],
        "source_system": child["source_system"],
        "latest_raw_event_id": child["latest_raw_event_id"],
        "latest_collected_at": child["latest_collected_at"],
        "attributes": {
            "parent_record_path": parent["record_path"],
            "child_record_path": child["record_path"],
            "raw_event_id": raw_event.get("id"),
        },
    }


def project_raw_event(raw_event: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    api_name = str(raw_event.get("api_name") or "")
    dataset_key = str(raw_event.get("dataset_key") or "")
    if not tables_for_api(api_name, dataset_key=dataset_key):
        return [], [], f"no response canonical registry for {dataset_key}/{api_name}"
    payload = raw_event.get("payload") or {}
    record = payload.get("raw")
    if not isinstance(record, dict):
        return [], [], "payload.raw must be an object"

    rows: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    def visit(current_record: dict[str, Any], record_path: str, parent_row: dict[str, Any] | None) -> None:
        entry = table_for_record(api_name, record_path, dataset_key=dataset_key)
        if entry is None:
            return
        row = _row_payload(
            raw_event=raw_event,
            record=current_record,
            record_path=record_path,
            entry=entry,
        )
        rows.append(row)
        if parent_row is not None:
            relationships.append(_relationship(parent_row, row, raw_event))
        for child_path, child_record in _child_records(current_record, record_path):
            visit(child_record, child_path, row)

    visit(record, "raw_event", None)
    return rows, relationships, None
