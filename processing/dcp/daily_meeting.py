"""DCP daily meeting normalizer."""

from datetime import datetime
from typing import Any


def _parse_epoch(timestamp: Any) -> float | None:
    try:
        return datetime.fromisoformat(str(timestamp).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def _float_value(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_present(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return value
    return None


def normalize_daily_meeting(
    raw_event: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    """Normalize one DCP daily meeting raw event into a work point entity."""
    if raw_event.get("dataset_key") != "daily_meeting":
        return None, "not daily_meeting dataset"
    if raw_event.get("collection") != "safePages":
        return None, "not safePages collection"
    if raw_event.get("page_name") not in {"meetingListAdmin", "站班会"}:
        return None, "not daily meeting page"
    if not raw_event.get("collected_at"):
        return None, "missing collected_at"
    collected_at_epoch = _parse_epoch(raw_event.get("collected_at"))
    if collected_at_epoch is None:
        return None, "invalid collected_at"

    payload = raw_event.get("payload") or {}
    raw = payload.get("raw")
    if not isinstance(raw, dict):
        return None, "payload.raw must be an object"

    longitude = _float_value(raw.get("toolBoxTalkLongitude"))
    latitude = _float_value(raw.get("toolBoxTalkLatitude"))
    if longitude is None or latitude is None:
        return None, "invalid toolBoxTalkLongitude/toolBoxTalkLatitude"

    work_point_id = _first_present(
        raw,
        "id",
        "toolBoxTalkId",
        "toolboxTalkId",
        "meetingId",
    ) or raw_event.get("source_record_id")
    if work_point_id in (None, ""):
        return None, "missing work point identity"
    work_date = _first_present(raw, "workDate", "work_date", "date")
    if work_date in (None, ""):
        return None, "missing work_date"

    attributes = {
        "project_name": _first_present(raw, "projectName", "prjName", "project_name"),
        "longitude": longitude,
        "latitude": latitude,
        "person_count": _first_present(
            raw,
            "currentConstrHeadcount",
            "personCount",
            "toolBoxTalkPersonCount",
            "workerCount",
        ),
        "risk_level": _first_present(
            raw, "reAssessmentRiskLevel", "riskLevel", "risk_level"
        ),
        "work_status": _first_present(
            raw, "currentConstructionStatus", "workStatus", "work_status"
        ),
        "voltage_level": _first_present(raw, "voltageLevel", "voltage_level"),
        "city": _first_present(raw, "buildUnitName", "city", "cityName"),
        "work_date": work_date,
        # Debug-only lineage snapshot. Consumer DTOs must not expose DCP raw fields directly.
        "raw": raw,
    }

    return {
        "entity_type": "work_point",
        "entity_key": f"dcp:work_point:{work_date}:{work_point_id}",
        "entity_date": work_date,
        "dataset_key": "daily_meeting",
        "source_system": raw_event.get("source_system"),
        "source_record_key": raw_event.get("source_record_key"),
        "latest_raw_event_id": raw_event.get("id"),
        "latest_collected_at": raw_event.get("collected_at"),
        "latest_collected_at_epoch": collected_at_epoch,
        "latest_source_record_hash": raw_event.get("source_record_hash"),
        "source_refs": [
            {
                "source_system": raw_event.get("source_system"),
                "dataset_key": raw_event.get("dataset_key"),
                "source_record_key": raw_event.get("source_record_key"),
                "source_record_id": raw_event.get("source_record_id"),
                "source_record_hash": raw_event.get("source_record_hash"),
                "raw_event_id": raw_event.get("id"),
            }
        ],
        "attributes": attributes,
    }, None
