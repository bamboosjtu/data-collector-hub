from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

import api.server as server
from core.plugin_manager import PluginManager
import processing.normalizer_runner as normalizer_runner
from processing.normalizer_runner import NormalizerRunner
from storage.sqlite_store import SQLiteStore


def _make_store() -> SQLiteStore:
    artifacts_dir = Path(__file__).resolve().parent / ".artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    db_path = artifacts_dir / f"processing-{uuid4().hex}.db"
    store = SQLiteStore(db_path)
    store.init_schema()
    manager = PluginManager()
    manager.discover_plugins()
    manager.save_discovered_plugins(store)
    return store


def _client(store: SQLiteStore) -> TestClient:
    server.store = store
    return TestClient(server.app)


def _epoch(timestamp: str) -> float:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()


def _station_event(
    suffix: str = "001",
    station_id: str | None = None,
    longitude: str = "116.391",
    latitude: str = "39.907",
    collected_at: str = "2026-05-03T21:30:12+08:00",
) -> dict:
    station_id = station_id or f"station-{suffix}"
    return {
        "schema_version": "source_event.v1",
        "event_id": f"evt-station-{suffix}",
        "idempotency_key": f"dcp:projectPages:变电站坐标:substation_coordinates:station-{suffix}",
        "source_system": "dcp",
        "source_event_type": "dcp.record",
        "event_granularity": "record",
        "source_record_id": f"station-{suffix}",
        "source_record_hash": f"hash-station-{suffix}",
        "occurred_at": "2026-05-03T21:30:12+08:00",
        "collected_at": collected_at,
        "payload": {
            "raw": {
                "id": station_id,
                "prjCode": "PRJ-001",
                "singleProjectCode": "SP-001",
                "longitude": longitude,
                "latitude": latitude,
                "extra": "kept in canonical raw attributes",
            }
        },
        "source_ref": {
            "collector": "vibe-downloader",
            "run_id": "20260503_213000",
            "collection": "projectPages",
            "page_name": "变电站坐标",
            "api_name": "substation_coordinates",
            "raw_data_index": 0,
            "record_index": 0,
            "record_path": "raw_data[0].records[0]",
            "source_file": f"projectPages/变电站坐标/station-{suffix}.json",
        },
    }


def _daily_meeting_event(suffix: str = "001", work_date: str = "2026-05-03") -> dict:
    return {
        "schema_version": "source_event.v1",
        "event_id": f"evt-daily-meeting-{suffix}",
        "idempotency_key": f"dcp:safePages:meetingListAdmin:queryToolBoxTalkListPagePc:meeting-{suffix}",
        "source_system": "dcp",
        "source_event_type": "dcp.record",
        "event_granularity": "record",
        "source_record_id": f"meeting-{suffix}",
        "source_record_hash": f"hash-daily-meeting-{suffix}",
        "occurred_at": "2026-05-03T08:30:00+08:00",
        "collected_at": "2026-05-03T21:30:12+08:00",
        "payload": {
            "raw": {
                "id": f"meeting-{suffix}",
                "projectName": "示例工程",
                "toolBoxTalkLongitude": "116.391",
                "toolBoxTalkLatitude": "39.907",
                "personCount": 12,
                "riskLevel": "medium",
                "workStatus": "working",
                "voltageLevel": "500kV",
                "city": "北京",
                "workDate": work_date,
                "rawOnly": "not exposed",
            }
        },
        "source_ref": {
            "collector": "vibe-downloader",
            "run_id": "20260503_213000",
            "collection": "safePages",
            "page_name": "meetingListAdmin",
            "api_name": "queryToolBoxTalkListPagePc",
            "raw_data_index": 0,
            "record_index": 0,
            "record_path": "raw_data[0].records[0]",
            "source_file": f"safePages/meetingListAdmin/{suffix}.json",
        },
    }


def _tower_event(
    suffix: str = "001",
    api_name: str = "tower_details",
    include_id: bool = True,
) -> dict:
    raw = {
        "singleProjectCode": "SP-TOWER-001",
        "biddingSectionCode": "BS-001",
        "towerNo": f"T-{suffix}",
        "upstreamTowerNo": "T-000",
        "longitudeEdit": "117.125",
        "latitudeEdit": "40.125",
        "longitude": "0",
        "latitude": "0",
        "towerType": "linear",
        "towerFullHeight": "66.5",
        "nominalHeight": "54",
        "rawOnly": "not exposed",
    }
    if include_id:
        raw["id"] = f"tower-{suffix}"
    return {
        "schema_version": "source_event.v1",
        "event_id": f"evt-tower-{suffix}",
        "idempotency_key": f"dcp:projectPages:杆塔信息:{api_name}:tower-{suffix}",
        "source_system": "dcp",
        "source_event_type": "dcp.record",
        "event_granularity": "record",
        "source_record_id": f"tower-{suffix}",
        "source_record_hash": f"hash-tower-{suffix}",
        "occurred_at": "2026-05-03T08:30:00+08:00",
        "collected_at": "2026-05-03T21:30:12+08:00",
        "payload": {"raw": raw},
        "source_ref": {
            "collector": "vibe-downloader",
            "run_id": "20260503_213000",
            "collection": "projectPages",
            "page_name": "杆塔信息",
            "api_name": api_name,
            "raw_data_index": 0,
            "record_index": 0,
            "record_path": "raw_data[0].records[0]",
            "source_file": f"projectPages/杆塔信息/{suffix}.json",
        },
    }


def test_station_source_event_to_sandbox_skeleton_flow():
    store = _make_store()
    client = _client(store)
    event = _station_event()

    ingestion = client.post("/ingestion/v1/events", json={"events": [event]})
    assert ingestion.status_code == 200
    assert ingestion.json()["accepted"] == 1

    processing = client.post("/processing/v1/run", json={"dataset_key": "station"})
    assert processing.status_code == 200
    assert processing.json()["processed"] == 1
    assert processing.json()["failed"] == 0

    entities = store.list_canonical_entities(entity_type="station", dataset_key="station")
    assert len(entities) == 1
    entity = entities[0]
    assert entity["entity_key"] == "dcp:station:SP-001"
    assert entity["attributes"]["project_code"] == "PRJ-001"
    assert entity["attributes"]["single_project_code"] == "SP-001"
    assert entity["attributes"]["dcp_coordinate_id"] == "station-001"
    assert entity["attributes"]["longitude"] == 116.391
    assert entity["attributes"]["latitude"] == 39.907
    assert entity["attributes"]["raw"]["extra"] == "kept in canonical raw attributes"
    assert entity["latest_source_record_hash"] == "hash-station-001"
    assert entity["source_refs"] == [
        {
            "source_system": "dcp",
            "dataset_key": "station",
            "source_record_key": event["idempotency_key"],
            "source_record_id": "station-001",
            "source_record_hash": "hash-station-001",
            "raw_event_id": entity["latest_raw_event_id"],
        }
    ]

    skeleton = client.get("/api/v1/sandbox/map/skeleton?limit=100")
    assert skeleton.status_code == 200
    body = skeleton.json()
    assert body["meta"] == {
        "limit": 100,
        "stations_count": 1,
        "towers_count": 0,
        "truncated": False,
    }
    assert body["towers"] == []
    assert body["lines"] == []
    assert body["stations"] == [
        {
            "id": "dcp:station:SP-001",
            "project_code": "PRJ-001",
            "single_project_code": "SP-001",
            "longitude": 116.391,
            "latitude": 39.907,
        }
    ]


def test_daily_meeting_source_event_to_work_point_and_summary():
    store = _make_store()
    client = _client(store)
    event = _daily_meeting_event()

    ingestion = client.post("/ingestion/v1/events", json={"events": [event]})
    assert ingestion.status_code == 200
    assert ingestion.json()["accepted"] == 1

    processing = client.post(
        "/processing/v1/run", json={"dataset_key": "daily_meeting"}
    )
    assert processing.status_code == 200
    assert processing.json()["processed"] == 1
    assert processing.json()["inserted"] == 1

    entities = store.list_canonical_entities(
        entity_type="work_point", dataset_key="daily_meeting"
    )
    assert len(entities) == 1
    entity = entities[0]
    assert entity["entity_key"] == "dcp:work_point:2026-05-03:meeting-001"
    assert entity["entity_date"] == "2026-05-03"
    assert entity["attributes"]["project_name"] == "示例工程"
    assert entity["attributes"]["longitude"] == 116.391
    assert entity["attributes"]["latitude"] == 39.907
    assert entity["attributes"]["person_count"] == 12
    assert entity["attributes"]["raw"]["rawOnly"] == "not exposed"

    summary = client.get("/api/v1/sandbox/map/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["meta"] == {
        "date": "2026-05-03",
        "limit": 10000,
        "work_points_count": 1,
        "truncated": False,
    }
    assert body["work_points"] == [
        {
            "id": "dcp:work_point:2026-05-03:meeting-001",
            "project_name": "示例工程",
            "longitude": 116.391,
            "latitude": 39.907,
            "person_count": 12,
            "risk_level": "medium",
            "work_status": "working",
            "voltage_level": "500kV",
            "city": "北京",
            "work_date": "2026-05-03",
        }
    ]
    assert "raw" not in body["work_points"][0]


def test_daily_meeting_same_id_on_different_dates_creates_two_work_points():
    store = _make_store()
    first = _daily_meeting_event("same-id-1", work_date="2026-05-03")
    second = _daily_meeting_event("same-id-2", work_date="2026-05-04")
    first["payload"]["raw"]["id"] = "meeting-same"
    second["payload"]["raw"]["id"] = "meeting-same"
    store.save_raw_event(first, dataset_key="daily_meeting")
    store.save_raw_event(second, dataset_key="daily_meeting")

    result = NormalizerRunner(store).run("daily_meeting")

    entities = store.list_canonical_entities(entity_type="work_point", limit=10)
    assert result["processed"] == 2
    assert {entity["entity_key"] for entity in entities} == {
        "dcp:work_point:2026-05-03:meeting-same",
        "dcp:work_point:2026-05-04:meeting-same",
    }


def test_sandbox_summary_filters_by_date_and_defaults_to_latest_date():
    store = _make_store()
    client = _client(store)
    first = _daily_meeting_event("date-1", work_date="2026-05-03")
    second = _daily_meeting_event("date-2", work_date="2026-05-04")
    first["payload"]["raw"]["projectName"] = "三号作业"
    second["payload"]["raw"]["projectName"] = "四号作业"
    store.save_raw_event(first, dataset_key="daily_meeting")
    store.save_raw_event(second, dataset_key="daily_meeting")
    NormalizerRunner(store).run("daily_meeting")

    filtered = client.get("/api/v1/sandbox/map/summary?date=2026-05-03")
    latest = client.get("/api/v1/sandbox/map/summary")

    assert filtered.status_code == 200
    assert filtered.json()["meta"]["date"] == "2026-05-03"
    assert filtered.json()["work_points"] == [
        {
            "id": "dcp:work_point:2026-05-03:meeting-date-1",
            "project_name": "三号作业",
            "longitude": 116.391,
            "latitude": 39.907,
            "person_count": 12,
            "risk_level": "medium",
            "work_status": "working",
            "voltage_level": "500kV",
            "city": "北京",
            "work_date": "2026-05-03",
        }
    ]
    assert latest.status_code == 200
    assert latest.json()["meta"]["date"] == "2026-05-04"
    assert latest.json()["work_points"][0]["project_name"] == "四号作业"


def test_daily_meeting_maps_current_monitor_fields():
    store = _make_store()
    event = _daily_meeting_event("field-map")
    raw = event["payload"]["raw"]
    raw["currentConstrHeadcount"] = 18
    raw["reAssessmentRiskLevel"] = "high"
    raw["currentConstructionStatus"] = "paused"
    raw["buildUnitName"] = "海淀"
    store.save_raw_event(event, dataset_key="daily_meeting")

    result = NormalizerRunner(store).run("daily_meeting")

    entity = store.list_canonical_entities(entity_type="work_point")[0]
    assert result["processed"] == 1
    assert entity["attributes"]["person_count"] == 18
    assert entity["attributes"]["risk_level"] == "high"
    assert entity["attributes"]["work_status"] == "paused"
    assert entity["attributes"]["city"] == "海淀"


def test_tower_details_source_event_to_tower_canonical():
    store = _make_store()
    client = _client(store)
    event = _tower_event()

    ingestion = client.post("/ingestion/v1/events", json={"events": [event]})
    assert ingestion.status_code == 200
    assert ingestion.json()["accepted"] == 1

    result = NormalizerRunner(store).run("tower")

    assert result["processed"] == 1
    assert result["inserted"] == 1
    entities = store.list_canonical_entities(entity_type="tower", dataset_key="tower")
    assert len(entities) == 1
    entity = entities[0]
    assert entity["entity_key"] == "dcp:tower:tower-001"
    assert entity["attributes"]["tower_id"] == "tower-001"
    assert entity["attributes"]["longitude"] == 117.125
    assert entity["attributes"]["latitude"] == 40.125
    assert entity["attributes"]["raw"]["rawOnly"] == "not exposed"


def test_tower_entity_key_falls_back_when_raw_id_missing():
    store = _make_store()
    event = _tower_event("fallback", include_id=False)
    store.save_raw_event(event, dataset_key="tower")

    result = NormalizerRunner(store).run("tower")

    entities = store.list_canonical_entities(entity_type="tower", dataset_key="tower")
    assert result["processed"] == 1
    assert entities[0]["entity_key"] == "dcp:tower:SP-TOWER-001:BS-001:T-fallback"
    assert entities[0]["attributes"]["single_project_code"] == "SP-TOWER-001"
    assert entities[0]["attributes"]["bidding_section_code"] == "BS-001"
    assert entities[0]["attributes"]["tower_no"] == "T-fallback"


def test_tower_single_projects_is_skipped_by_tower_normalizer():
    store = _make_store()
    client = _client(store)
    event = _tower_event("single-project", api_name="tower_single_projects")

    ingestion = client.post("/ingestion/v1/events", json={"events": [event]})
    assert ingestion.status_code == 200
    assert ingestion.json()["accepted"] == 1

    result = NormalizerRunner(store).run("tower")

    assert result["processed"] == 0
    assert result["skipped"] == 1
    assert "not tower_details api" in result["errors"][0]
    assert store.list_canonical_entities(entity_type="tower", dataset_key="tower") == []


def test_sandbox_skeleton_returns_towers_and_stations_without_raw():
    store = _make_store()
    client = _client(store)
    station_event = _station_event()
    tower_event = _tower_event()

    assert client.post("/ingestion/v1/events", json={"events": [station_event]}).json()[
        "accepted"
    ] == 1
    assert client.post("/ingestion/v1/events", json={"events": [tower_event]}).json()[
        "accepted"
    ] == 1
    assert NormalizerRunner(store).run("station")["processed"] == 1
    assert NormalizerRunner(store).run("tower")["processed"] == 1

    response = client.get("/api/v1/sandbox/map/skeleton")

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["stations_count"] == 1
    assert body["meta"]["towers_count"] == 1
    assert body["lines"] == []
    assert body["stations"][0]["id"] == "dcp:station:SP-001"
    assert body["towers"][0]["id"] == "dcp:tower:tower-001"
    assert body["towers"][0]["longitude"] == 117.125
    assert body["towers"][0]["latitude"] == 40.125
    assert "raw" not in body["stations"][0]
    assert "raw" not in body["towers"][0]


def test_processing_run_supports_station_from_registry():
    store = _make_store()
    client = _client(store)

    response = client.post("/processing/v1/run", json={"dataset_key": "station"})

    assert response.status_code == 200
    assert response.json()["processed"] == 0
    assert response.json()["failed"] == 0


def test_processing_run_unknown_dataset_returns_supported_dataset_keys():
    store = _make_store()
    client = _client(store)

    response = client.post("/processing/v1/run", json={"dataset_key": "unknown_dataset"})

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["error"] == "unsupported dataset_key: unknown_dataset"
    assert set(detail["supported_datasets"]) == {"daily_meeting", "tower", "station"}


def test_station_entity_key_prefers_single_project_code():
    store = _make_store()
    event = _station_event(suffix="key-preferred", station_id="coord-001")
    store.save_raw_event(event, dataset_key="station")

    result = NormalizerRunner(store).run("station")

    assert result["processed"] == 1
    entities = store.list_canonical_entities(entity_type="station", dataset_key="station")
    assert entities[0]["entity_key"] == "dcp:station:SP-001"
    assert entities[0]["attributes"]["dcp_coordinate_id"] == "coord-001"


def test_station_entity_key_falls_back_to_coordinate_id_without_single_project_code():
    store = _make_store()
    event = _station_event(suffix="key-fallback", station_id="coord-fallback")
    del event["payload"]["raw"]["singleProjectCode"]
    store.save_raw_event(event, dataset_key="station")

    result = NormalizerRunner(store).run("station")

    assert result["processed"] == 1
    entities = store.list_canonical_entities(entity_type="station", dataset_key="station")
    assert entities[0]["entity_key"] == "dcp:station:coord-fallback"
    assert entities[0]["attributes"]["single_project_code"] is None
    assert entities[0]["attributes"]["dcp_coordinate_id"] == "coord-fallback"


def test_station_normalizer_processes_more_than_default_page_size():
    store = _make_store()
    for index in range(1001):
        event = _station_event(suffix=f"{index:04d}")
        event["payload"]["raw"]["singleProjectCode"] = f"SP-{index:04d}"
        store.save_raw_event(event, dataset_key="station")

    result = NormalizerRunner(store).run("station", batch_size=100)

    assert result["processed"] == 1001
    assert result["failed"] == 0
    assert len(store.list_canonical_entities(entity_type="station", limit=2000)) == 1001


def test_older_station_raw_event_does_not_overwrite_newer_current_entity():
    store = _make_store()
    newer = _station_event(
        suffix="newer",
        station_id="station-versioned",
        longitude="120.5",
        latitude="30.5",
        collected_at="2026-05-03T22:30:12+08:00",
    )
    older = _station_event(
        suffix="older",
        station_id="station-versioned",
        longitude="100.5",
        latitude="20.5",
        collected_at="2026-05-03T21:30:12+08:00",
    )
    store.save_raw_event(newer, dataset_key="station")
    store.save_raw_event(older, dataset_key="station")

    result = NormalizerRunner(store).run("station")

    assert result["processed"] == 2
    entities = store.list_canonical_entities(entity_type="station", dataset_key="station")
    assert len(entities) == 1
    entity = entities[0]
    assert entity["latest_collected_at"] == newer["collected_at"]
    assert entity["latest_source_record_hash"] == newer["source_record_hash"]
    assert entity["attributes"]["longitude"] == 120.5
    assert entity["attributes"]["latitude"] == 30.5
    assert result["inserted"] == 1
    assert result["ignored_older"] == 1


def test_canonical_upsert_compares_latest_collected_at_epoch_not_strings():
    store = _make_store()
    store.upsert_canonical_entity(
        entity_type="station",
        entity_key="dcp:station:timezone",
        dataset_key="station",
        source_system="dcp",
        source_record_key="dcp:station:timezone-old",
        latest_raw_event_id=1,
        latest_collected_at="2026-05-03T16:30:00+08:00",
        latest_collected_at_epoch=_epoch("2026-05-03T16:30:00+08:00"),
        latest_source_record_hash="hash-timezone-old",
        source_refs=[
            {
                "source_system": "dcp",
                "dataset_key": "station",
                "source_record_key": "dcp:station:timezone-old",
            }
        ],
        attributes={"longitude": 116.0, "latitude": 39.0},
    )

    status = store.upsert_canonical_entity(
        entity_type="station",
        entity_key="dcp:station:timezone",
        dataset_key="station",
        source_system="dcp",
        source_record_key="dcp:station:timezone-new",
        latest_raw_event_id=2,
        latest_collected_at="2026-05-03T09:00:00Z",
        latest_collected_at_epoch=_epoch("2026-05-03T09:00:00Z"),
        latest_source_record_hash="hash-timezone-new",
        source_refs=[
            {
                "source_system": "dcp",
                "dataset_key": "station",
                "source_record_key": "dcp:station:timezone-new",
            }
        ],
        attributes={"longitude": 117.0, "latitude": 40.0},
    )

    entity = store.list_canonical_entities(entity_type="station", dataset_key="station")[0]
    assert status == "updated"
    assert entity["latest_collected_at"] == "2026-05-03T09:00:00Z"
    assert entity["latest_source_record_hash"] == "hash-timezone-new"
    assert entity["attributes"]["longitude"] == 117.0


def test_incremental_mode_second_run_does_not_reprocess_raw_events():
    store = _make_store()
    event = _station_event(suffix="incremental")
    store.save_raw_event(event, dataset_key="station")

    first = NormalizerRunner(store).run("station")
    second = NormalizerRunner(store).run("station")

    assert first["processed"] == 1
    assert first["inserted"] == 1
    assert second["processed"] == 0
    assert second["inserted"] == 0
    assert second["updated"] == 0
    assert second["ignored_older"] == 0
    assert second["last_raw_event_id"] == first["last_raw_event_id"]


def test_full_mode_rescans_all_raw_events():
    store = _make_store()
    event = _station_event(suffix="full")
    store.save_raw_event(event, dataset_key="station")

    first = NormalizerRunner(store).run("station")
    second = NormalizerRunner(store).run("station", mode="full")

    assert first["processed"] == 1
    assert second["processed"] == 1
    assert second["updated"] == 1
    assert second["last_raw_event_id"] == first["last_raw_event_id"]


def test_normalizer_state_records_last_raw_event_id():
    store = _make_store()
    first_event = _station_event(suffix="state-1")
    second_event = _station_event(suffix="state-2")
    second_event["payload"]["raw"]["singleProjectCode"] = "SP-STATE-2"
    store.save_raw_event(first_event, dataset_key="station")
    _, second_raw_event_id = store.save_raw_event(second_event, dataset_key="station")

    result = NormalizerRunner(store).run("station", batch_size=1)

    state = store.get_normalizer_state("station")
    assert result["processed"] == 2
    assert result["last_raw_event_id"] == second_raw_event_id
    assert state["last_raw_event_id"] == second_raw_event_id
    assert state["normalizer_version"] == "station.v1"


def test_normalizer_run_saves_current_version():
    store = _make_store()
    event = _station_event(suffix="state-version")
    store.save_raw_event(event, dataset_key="station")

    result = NormalizerRunner(store).run("station")

    state = store.get_normalizer_state("station")
    assert result["processed"] == 1
    assert state["normalizer_version"] == "station.v1"


def test_normalizer_version_change_reprocesses_from_zero(monkeypatch):
    store = _make_store()
    event = _station_event(suffix="version-change")
    store.save_raw_event(event, dataset_key="station")

    first = NormalizerRunner(store).run("station")
    handler = normalizer_runner.NORMALIZERS["station"]["handler"]
    monkeypatch.setitem(
        normalizer_runner.NORMALIZERS,
        "station",
        {
            "version": "station.v2",
            "handler": handler,
        },
    )
    second = NormalizerRunner(store).run("station")

    state = store.get_normalizer_state("station")
    assert first["processed"] == 1
    assert second["processed"] == 1
    assert second["updated"] == 1
    assert state["normalizer_version"] == "station.v2"


def test_incremental_checkpoint_advances_past_skipped_non_target_api():
    store = _make_store()
    skipped_event = _station_event(suffix="skip-api")
    skipped_event["source_ref"]["api_name"] = "substation_single_projects"
    skipped_event["idempotency_key"] = (
        "dcp:projectPages:变电站坐标:substation_single_projects:skip-api"
    )
    processed_event = _station_event(suffix="after-skip")
    processed_event["payload"]["raw"]["singleProjectCode"] = "SP-AFTER-SKIP"
    store.save_raw_event(skipped_event, dataset_key="station")
    _, processed_raw_event_id = store.save_raw_event(processed_event, dataset_key="station")

    result = NormalizerRunner(store).run("station")

    assert result["processed"] == 1
    assert result["skipped"] == 1
    assert result["failed"] == 0
    assert result["last_raw_event_id"] == processed_raw_event_id
    assert store.get_normalizer_state("station")["last_raw_event_id"] == processed_raw_event_id


def test_incremental_checkpoint_does_not_advance_past_failed_raw_event():
    first_event = _station_event(suffix="checkpoint-success")
    second_event = _station_event(suffix="checkpoint-failure")

    raw_events = []
    for raw_event_id, event in enumerate([first_event, second_event], start=1):
        raw_events.append(
            {
                "id": raw_event_id,
                "dataset_key": "station",
                "api_name": "substation_coordinates",
                "collected_at": event["collected_at"],
                "source_system": event["source_system"],
                "source_record_key": event["idempotency_key"],
                "source_record_id": event["source_record_id"],
                "source_record_hash": event["source_record_hash"],
                "payload": event["payload"],
            }
        )

    class StoreWithSecondUpsertFailure:
        def __init__(self):
            self.state = {"last_raw_event_id": 0}
            self.upsert_count = 0

        def get_normalizer_state(self, _dataset_key):
            return self.state

        def save_normalizer_state(
            self, _dataset_key, last_raw_event_id, normalizer_version
        ):
            self.state = {
                "last_raw_event_id": last_raw_event_id,
                "normalizer_version": normalizer_version,
            }

        def list_raw_events(self, dataset_key, limit=1000, offset=0, after_id=None):
            after_id = after_id or 0
            return [event for event in raw_events if event["id"] > after_id]

        def upsert_canonical_entity(self, **_entity):
            self.upsert_count += 1
            if self.upsert_count == 2:
                raise RuntimeError("boom")
            return "inserted"

    store = StoreWithSecondUpsertFailure()
    result = NormalizerRunner(store).run("station")

    assert result["processed"] == 1
    assert result["failed"] == 1
    assert result["last_raw_event_id"] <= 1
    assert store.state["last_raw_event_id"] <= 1
    assert "boom" in result["errors"][0]


def test_station_normalizer_skips_invalid_collected_at():
    event = _station_event(suffix="invalid-collected-at")
    raw_event = {
        "id": 1,
        "dataset_key": "station",
        "api_name": "substation_coordinates",
        "collected_at": "not-a-datetime",
        "source_system": event["source_system"],
        "source_record_key": event["idempotency_key"],
        "source_record_id": event["source_record_id"],
        "source_record_hash": event["source_record_hash"],
        "payload": event["payload"],
    }

    class StoreWithInvalidCollectedAt:
        def __init__(self):
            self.calls = 0

        def get_normalizer_state(self, _dataset_key):
            return {"last_raw_event_id": 0}

        def save_normalizer_state(
            self, _dataset_key, _last_raw_event_id, _normalizer_version
        ):
            pass

        def list_raw_events(self, dataset_key, limit=1000, offset=0, after_id=None):
            self.calls += 1
            return [raw_event] if self.calls == 1 else []

        def upsert_canonical_entity(self, **_entity):
            raise AssertionError("invalid collected_at event must not be upserted")

    result = NormalizerRunner(StoreWithInvalidCollectedAt()).run("station")

    assert result["processed"] == 0
    assert result["skipped"] == 1
    assert "invalid collected_at" in result["errors"][0]


def test_incoming_missing_latest_collected_at_does_not_overwrite_current_entity():
    store = _make_store()
    source_ref = {
        "source_system": "dcp",
        "dataset_key": "station",
        "source_record_key": "dcp:station:current",
    }
    store.upsert_canonical_entity(
        entity_type="station",
        entity_key="dcp:station:current",
        dataset_key="station",
        source_system="dcp",
        source_record_key="dcp:station:current",
        latest_raw_event_id=1,
        latest_collected_at="2026-05-03T22:30:12+08:00",
        latest_collected_at_epoch=_epoch("2026-05-03T22:30:12+08:00"),
        latest_source_record_hash="hash-current",
        source_refs=[source_ref],
        attributes={"longitude": 120.5, "latitude": 30.5},
    )

    store.upsert_canonical_entity(
        entity_type="station",
        entity_key="dcp:station:current",
        dataset_key="station",
        source_system="dcp",
        source_record_key="dcp:station:missing-time",
        latest_raw_event_id=2,
        latest_collected_at=None,
        latest_collected_at_epoch=None,
        latest_source_record_hash="hash-missing-time",
        source_refs=[
            {
                "source_system": "dcp",
                "dataset_key": "station",
                "source_record_key": "dcp:station:missing-time",
            }
        ],
        attributes={"longitude": 100.5, "latitude": 20.5},
    )

    entity = store.list_canonical_entities(entity_type="station", dataset_key="station")[0]
    assert entity["latest_collected_at"] == "2026-05-03T22:30:12+08:00"
    assert entity["latest_source_record_hash"] == "hash-current"
    assert entity["source_record_key"] == "dcp:station:current"
    assert entity["attributes"]["longitude"] == 120.5
    assert entity["source_refs"] == [source_ref]


def test_source_refs_are_merged_across_current_entity_upserts():
    store = _make_store()
    first_ref = {
        "source_system": "dcp",
        "dataset_key": "station",
        "source_record_key": "dcp:station:first",
    }
    second_ref = {
        "source_system": "dcp",
        "dataset_key": "station",
        "source_record_key": "dcp:station:second",
    }
    store.upsert_canonical_entity(
        entity_type="station",
        entity_key="dcp:station:merged",
        dataset_key="station",
        source_system="dcp",
        source_record_key="dcp:station:first",
        latest_raw_event_id=1,
        latest_collected_at="2026-05-03T21:30:12+08:00",
        latest_collected_at_epoch=_epoch("2026-05-03T21:30:12+08:00"),
        latest_source_record_hash="hash-first",
        source_refs=[first_ref],
        attributes={"longitude": 116.0, "latitude": 39.0},
    )

    store.upsert_canonical_entity(
        entity_type="station",
        entity_key="dcp:station:merged",
        dataset_key="station",
        source_system="dcp",
        source_record_key="dcp:station:second",
        latest_raw_event_id=2,
        latest_collected_at="2026-05-03T22:30:12+08:00",
        latest_collected_at_epoch=_epoch("2026-05-03T22:30:12+08:00"),
        latest_source_record_hash="hash-second",
        source_refs=[second_ref],
        attributes={"longitude": 117.0, "latitude": 40.0},
    )

    entity = store.list_canonical_entities(entity_type="station", dataset_key="station")[0]
    source_record_keys = {
        ref["source_record_key"] for ref in entity["source_refs"]
    }
    assert source_record_keys == {"dcp:station:first", "dcp:station:second"}
    assert entity["latest_source_record_hash"] == "hash-second"
    assert entity["attributes"]["longitude"] == 117.0


def test_sandbox_skeleton_reports_truncated_when_over_limit():
    store = _make_store()
    client = _client(store)
    for index in range(2):
        store.upsert_canonical_entity(
            entity_type="station",
            entity_key=f"dcp:station:limit-{index}",
            dataset_key="station",
            source_system="dcp",
            source_record_key=f"dcp:station:limit-{index}",
            latest_raw_event_id=index + 1,
            latest_collected_at=f"2026-05-03T22:30:1{index}+08:00",
            latest_collected_at_epoch=_epoch(f"2026-05-03T22:30:1{index}+08:00"),
            latest_source_record_hash=f"hash-limit-{index}",
            source_refs=[
                {
                    "source_system": "dcp",
                    "dataset_key": "station",
                    "source_record_key": f"dcp:station:limit-{index}",
                }
            ],
            attributes={
                "project_code": "PRJ-001",
                "single_project_code": f"SP-LIMIT-{index}",
                "longitude": 116.0 + index,
                "latitude": 39.0 + index,
            },
        )

    response = client.get("/api/v1/sandbox/map/skeleton?limit=1")

    assert response.status_code == 200
    body = response.json()
    assert body["meta"] == {
        "limit": 1,
        "stations_count": 1,
        "towers_count": 0,
        "truncated": True,
    }
    assert len(body["stations"]) == 1


def test_station_normalizer_skips_raw_event_missing_collected_at():
    event = _station_event(suffix="missing-collected-at")
    raw_event = {
        "id": 1,
        "dataset_key": "station",
        "api_name": "substation_coordinates",
        "source_system": event["source_system"],
        "source_record_key": event["idempotency_key"],
        "source_record_id": event["source_record_id"],
        "source_record_hash": event["source_record_hash"],
        "payload": event["payload"],
    }

    class StoreWithMissingCollectedAt:
        def __init__(self):
            self.calls = 0

        def get_normalizer_state(self, _dataset_key):
            return {"last_raw_event_id": 0}

        def save_normalizer_state(
            self, _dataset_key, _last_raw_event_id, _normalizer_version
        ):
            pass

        def list_raw_events(self, dataset_key, limit=1000, offset=0, after_id=None):
            self.calls += 1
            return [raw_event] if self.calls == 1 else []

        def upsert_canonical_entity(self, **_entity):
            raise AssertionError("missing collected_at event must not be upserted")

    result = NormalizerRunner(StoreWithMissingCollectedAt()).run("station")

    assert result["processed"] == 0
    assert result["skipped"] == 1
    assert result["failed"] == 0
    assert "missing collected_at" in result["errors"][0]


def test_unsupported_dataset_key_fails_via_registry():
    store = _make_store()

    result = NormalizerRunner(store).run("unknown_dataset")

    assert result["processed"] == 0
    assert result["skipped"] == 0
    assert result["failed"] == 1
    assert result["errors"] == ["unsupported dataset_key: unknown_dataset"]
