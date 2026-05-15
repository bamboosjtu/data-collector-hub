from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from core.plugin_manager import PluginManager
from processing.normalizer_runner import NormalizerRunner
from storage.sqlite_store import SQLiteStore
from conftest import seed_test_records


def _make_store() -> SQLiteStore:
    artifacts_dir = Path(__file__).resolve().parent / ".artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    db_path = artifacts_dir / f"typed-store-{uuid4().hex}.db"
    store = SQLiteStore(db_path)
    store.init_schema()
    manager = PluginManager()
    manager.discover_plugins()
    manager.save_discovered_plugins(store)
    return store


def _daily_event(*, suffix: str, collected_at: str, work_date: str, headcount: int) -> dict:
    return {
        "raw_event_id": f"raw-daily-{suffix}",
        "idempotency_key": f"dcp:safePages:meeting:{suffix}",
        "source_system": "dcp",
        "source_record_id": f"meeting-{suffix}",
        "source_record_hash": f"hash-{suffix}",
        "occurred_at": collected_at,
        "collected_at": collected_at,
        "payload": {
            "raw": {
                "id": "meeting-001",
                "currentConstrDate": work_date,
                "projectName": "示例工程",
                "prjCode": "PRJ-001",
                "singleProjectCode": "SP-001",
                "biddingSectionCode": "BS-001",
                "currentConstrHeadcount": headcount,
                "reAssessmentRiskLevel": "high",
                "currentConstructionStatus": "working",
                "toolBoxTalkLongitude": 112.9,
                "toolBoxTalkLatitude": 28.2,
                "voltageLevel": "220kV",
                "buildUnitName": "长沙",
            }
        },
        "source_ref": {
            "collector": "vibe-downloader",
            "collection": "safePages",
            "page_name": "meetingListAdmin",
            "api_name": "queryToolBoxTalkListPagePc",
            "record_path": "raw_data[0].records[0]",
            "source_file": f"daily_meeting/{work_date}.json",
            "context": {"work_date": work_date},
        },
    }


def test_typed_current_entity_keeps_latest_but_observations_append() -> None:
    store = _make_store()
    seed_test_records(
        store,
        "daily_meeting",
        [
            _daily_event(
                suffix="old",
                collected_at="2026-05-08T09:00:00+08:00",
                work_date="2026-05-08",
                headcount=8,
            ),
            _daily_event(
                suffix="new",
                collected_at="2026-05-08T10:00:00+08:00",
                work_date="2026-05-08",
                headcount=12,
            ),
        ],
    )

    result = NormalizerRunner(store).run("daily_meeting", mode="full")

    assert result["failed"] == 0
    entity = store.list_canonical_current_entities(entity_type="work_point", limit=1)[0]
    assert entity["attributes"]["person_count"] == 12
    observations = store.list_canonical_entity_observations(
        entity_type="work_point",
        entity_key=entity["entity_key"],
        limit=10,
    )
    assert len(observations) == 2
    assert {
        item["attributes_snapshot"]["person_count"]
        for item in observations
    } == {8, 12}


def test_project_hierarchy_entities_land_in_typed_tables() -> None:
    store = _make_store()
    seed_test_records(
        store,
        "project_preconstruction",
        [
            {
                "raw_event_id": "raw-project-001",
                "idempotency_key": "dcp:projectPages:项目前期成果:preconstruction_results_detail:001",
                "source_system": "dcp",
                "source_record_id": "project-001",
                "source_record_hash": "hash-project-001",
                "occurred_at": "2026-05-08T08:00:00+08:00",
                "collected_at": "2026-05-08T08:00:00+08:00",
                "payload": {
                    "raw": {
                        "prjCode": "PRJ-001",
                        "prjName": "示例工程",
                        "sinList": [
                            {
                                "singleProjectCode": "SP-001",
                                "singleProjectName": "单项一",
                                "bidSectList": [
                                    {
                                        "biddingSectionCode": "BS-001",
                                        "biddingSectionName": "标段一",
                                    }
                                ],
                            }
                        ],
                    }
                },
                "source_ref": {
                    "collector": "vibe-downloader",
                    "collection": "projectPages",
                    "page_name": "项目前期成果",
                    "api_name": "preconstruction_results_detail",
                    "record_path": "raw_data[0].records[0]",
                    "source_file": "project_preconstruction/001.json",
                },
            }
        ],
    )

    result = NormalizerRunner(store).run("project_hierarchy", mode="full")

    assert result["inserted"] == 3
    assert store.list_domain_entities("project", limit=10)[0]["attributes"]["project_code"] == "PRJ-001"
    assert store.list_domain_entities("single_project", limit=10)[0]["attributes"]["single_project_code"] == "SP-001"
    assert store.list_domain_entities("bidding_section", limit=10)[0]["attributes"]["bidding_section_code"] == "BS-001"
