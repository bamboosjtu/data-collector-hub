from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from core.plugin_manager import PluginManager
from processing.normalizer_runner import NormalizerRunner
from storage.sqlite_store import SQLiteStore


def _make_store() -> SQLiteStore:
    artifacts_dir = Path(__file__).resolve().parent / ".artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    db_path = artifacts_dir / f"dcp-domain-{uuid4().hex}.db"
    store = SQLiteStore(db_path)
    store.init_schema()
    manager = PluginManager()
    manager.discover_plugins()
    manager.save_discovered_plugins(store)
    return store


def _event(
    *,
    suffix: str,
    dataset_key: str,
    page_name: str,
    api_name: str,
    raw: dict,
) -> dict:
    return {
        "schema_version": "source_event.v1",
        "event_id": f"evt-{dataset_key}-{suffix}",
        "idempotency_key": f"dcp:projectPages:{page_name}:{api_name}:{suffix}",
        "source_system": "dcp",
        "source_event_type": "dcp.record",
        "event_granularity": "record",
        "source_record_id": f"record-{suffix}",
        "source_record_hash": f"hash-{suffix}",
        "occurred_at": "2026-05-03T08:30:00+08:00",
        "collected_at": "2026-05-03T21:30:12+08:00",
        "payload": {"raw": raw},
        "source_ref": {
            "collector": "vibe-downloader",
            "run_id": "20260503_213000",
            "collection": "projectPages",
            "page_name": page_name,
            "api_name": api_name,
            "raw_data_index": 0,
            "record_index": 0,
            "record_path": "raw_data[0].records[0]",
            "source_file": f"projectPages/{page_name}/{suffix}.json",
        },
    }


def test_one_raw_event_can_generate_multiple_entities_and_relationships() -> None:
    store = _make_store()
    event = _event(
        suffix="hierarchy",
        dataset_key="project_preconstruction",
        page_name="项目前期成果",
        api_name="preconstruction_results_detail",
        raw={
            "prjCode": "PRJ-001",
            "prjName": "项目一",
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
        },
    )
    store.save_raw_event(event, dataset_key="project_preconstruction")

    result = NormalizerRunner(store).run("project_hierarchy")

    assert result["inserted"] == 3
    assert result["relationships_inserted"] == 2
    assert store.list_canonical_entities(entity_type="project")[0]["entity_key"] == "dcp:project:PRJ-001"
    relationships = store.list_canonical_relationships(limit=10)
    assert {item["relationship_type"] for item in relationships} == {
        "HAS_SINGLE_PROJECT",
        "HAS_BIDDING_SECTION",
    }


def test_section_single_projects_generates_single_project_and_bidding_section() -> None:
    store = _make_store()
    event = _event(
        suffix="section-single",
        dataset_key="line_section",
        page_name="区段划分",
        api_name="section_single_projects",
        raw={
            "prjCode": "PRJ-002",
            "singleProjectCode": "SP-002",
            "singleProjectName": "区段单项",
            "sectList": [
                {
                    "biddingSectionCode": "BS-002",
                    "biddingSectionName": "区段标段",
                }
            ],
        },
    )
    store.save_raw_event(event, dataset_key="line_section")

    result = NormalizerRunner(store).run("line_section")

    assert result["inserted"] == 2
    assert result["relationships_inserted"] == 1
    assert store.list_canonical_entities(entity_type="single_project")[0]["entity_key"] == "dcp:single_project:SP-002"
    assert store.list_canonical_entities(entity_type="bidding_section")[0]["entity_key"] == "dcp:bidding_section:BS-002"


def test_section_details_generates_line_section_and_tower_sequence_relationships() -> None:
    store = _make_store()
    event = _event(
        suffix="section-details",
        dataset_key="line_section",
        page_name="区段划分",
        api_name="section_details",
        raw={
            "id": "LS-001",
            "sectionName": "一区段",
            "prjCode": "PRJ-003",
            "singleProjectCode": "SP-003",
            "biddingSectionCode": "BS-003",
            "sectionVo": {"towerNoList": ["T001", "T002"]},
        },
    )
    store.save_raw_event(event, dataset_key="line_section")

    result = NormalizerRunner(store).run("line_section")

    assert result["inserted"] >= 1
    assert result["relationships_inserted"] >= 2
    line_section = store.list_canonical_entities(entity_type="line_section")[0]
    assert line_section["entity_key"] == "dcp:line_section:LS-001"
    tower_sequence = store.list_canonical_relationships(
        relationship_type="HAS_TOWER_SEQUENCE",
        limit=10,
    )
    assert [item["attributes"]["tower_no"] for item in tower_sequence] == ["T002", "T001"]


def test_section_details_missing_context_marks_known_issue_without_fake_hierarchy() -> None:
    store = _make_store()
    event = _event(
        suffix="section-details-missing-context",
        dataset_key="line_section",
        page_name="区段划分",
        api_name="section_details",
        raw={
            "id": "LS-002",
            "sectionName": "二区段",
            "sectionVo": {"towerNoList": ["T009"]},
        },
    )
    store.save_raw_event(event, dataset_key="line_section")

    result = NormalizerRunner(store).run("line_section")

    assert result["inserted"] == 1
    line_section = store.list_canonical_entities(entity_type="line_section")[0]
    assert line_section["attributes"]["known_issues"]
    assert store.list_canonical_entities(entity_type="single_project") == []
    assert store.list_canonical_entities(entity_type="bidding_section") == []


def test_year_progress_generates_project_progress_and_project_relationship() -> None:
    store = _make_store()
    event = _event(
        suffix="year-progress",
        dataset_key="year_progress",
        page_name="年度进度计划分析",
        api_name="yearly_progress_analysis",
        raw={
            "id": "PROG-001",
            "prjCode": "PRJ-004",
            "prjName": "年度项目",
            "singleList": [
                {
                    "singleProjectCode": "SP-004",
                    "singleProjectName": "年度单项",
                }
            ],
        },
    )
    store.save_raw_event(event, dataset_key="year_progress")

    result = NormalizerRunner(store).run("year_progress")

    assert result["inserted"] == 3
    assert result["relationships_inserted"] == 2
    progress = store.list_canonical_entities(entity_type="project_progress")[0]
    assert progress["entity_key"] == "dcp:project_progress:PROG-001"
    relationship = store.list_canonical_relationships(
        relationship_type="HAS_PROJECT_PROGRESS"
    )[0]
    assert relationship["from_entity_key"] == "dcp:project:PRJ-004"
    assert store.list_canonical_entities(entity_type="bidding_section") == []


def test_year_progress_without_project_code_skips_with_summary() -> None:
    store = _make_store()
    event = _event(
        suffix="year-progress-skip",
        dataset_key="year_progress",
        page_name="年度进度计划分析",
        api_name="yearly_progress_analysis",
        raw={"id": "PROG-002", "projectName": "字段不明确"},
    )
    store.save_raw_event(event, dataset_key="year_progress")

    result = NormalizerRunner(store).run("year_progress")

    assert result["skipped"] == 1
    assert result["inserted"] == 0
    assert "yearly_progress_analysis missing prjCode" in result["errors"][0]


def test_canonical_relationship_store_get_and_list() -> None:
    store = _make_store()
    status = store.upsert_canonical_relationship(
        relationship_key="rel-1",
        relationship_type="HAS_SINGLE_PROJECT",
        from_entity_type="project",
        from_entity_key="dcp:project:PRJ-005",
        to_entity_type="single_project",
        to_entity_key="dcp:single_project:SP-005",
        dataset_key="line_section",
        source_system="dcp",
        latest_raw_event_id=1,
        latest_collected_at="2026-05-03T21:30:12+08:00",
        attributes={"source": "test"},
    )

    assert status == "inserted"
    assert store.get_canonical_relationship("rel-1")["attributes"] == {"source": "test"}
    assert len(store.list_canonical_relationships(from_entity_key="dcp:project:PRJ-005")) == 1


def test_domain_canonical_acceptance_entities_and_relationships_land_in_store() -> None:
    store = _make_store()
    store.save_raw_event(
        _event(
            suffix="accept-hierarchy",
            dataset_key="project_preconstruction",
            page_name="项目前期成果",
            api_name="preconstruction_results_detail",
            raw={
                "prjCode": "PRJ-ACCEPT",
                "prjName": "验收项目",
                "sinList": [
                    {
                        "singleProjectCode": "SP-ACCEPT",
                        "singleProjectName": "验收单项",
                        "bidSectList": [
                            {
                                "biddingSectionCode": "BS-ACCEPT",
                                "biddingSectionName": "验收标段",
                            }
                        ],
                    }
                ],
            },
        ),
        dataset_key="project_preconstruction",
    )
    store.save_raw_event(
        _event(
            suffix="accept-section",
            dataset_key="line_section",
            page_name="区段划分",
            api_name="section_details",
            raw={
                "id": "LS-ACCEPT",
                "sectionName": "验收区段",
                "prjCode": "PRJ-ACCEPT",
                "singleProjectCode": "SP-ACCEPT",
                "biddingSectionCode": "BS-ACCEPT",
                "sectionVo": {"towerNoList": ["T001"]},
            },
        ),
        dataset_key="line_section",
    )
    store.save_raw_event(
        _event(
            suffix="accept-progress",
            dataset_key="year_progress",
            page_name="年度进度计划分析",
            api_name="yearly_progress_analysis",
            raw={
                "id": "PROG-ACCEPT",
                "prjCode": "PRJ-ACCEPT",
                "planYear": "2026",
            },
        ),
        dataset_key="year_progress",
    )

    hierarchy_result = NormalizerRunner(store).run("project_hierarchy", mode="full")
    line_result = NormalizerRunner(store).run("line_section", mode="full")
    progress_result = NormalizerRunner(store).run("year_progress", mode="full")

    assert hierarchy_result["failed"] == 0
    assert line_result["failed"] == 0
    assert progress_result["failed"] == 0
    entity_types = {
        item["entity_type"]
        for item in store.list_canonical_entities(dataset_key=None, limit=100)
    }
    assert {
        "project",
        "single_project",
        "bidding_section",
        "line_section",
        "project_progress",
    }.issubset(entity_types)
    relationship_types = {
        item["relationship_type"]
        for item in store.list_canonical_relationships(limit=100)
    }
    assert {
        "HAS_SINGLE_PROJECT",
        "HAS_BIDDING_SECTION",
        "HAS_TOWER_SEQUENCE",
        "HAS_PROJECT_PROGRESS",
    }.issubset(relationship_types)
