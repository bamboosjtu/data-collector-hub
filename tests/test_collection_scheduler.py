from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

import api.server as server
from core.plugin_manager import PluginManager
from storage.sqlite_store import SQLiteStore


def _make_registered_store() -> SQLiteStore:
    artifacts_dir = Path(__file__).resolve().parent / ".artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    db_path = artifacts_dir / f"collection-scheduler-{uuid4().hex}.db"
    store = SQLiteStore(db_path)
    store.init_schema()

    manager = PluginManager()
    manager.discover_plugins()
    manager.save_discovered_plugins(store)
    return store


def _client(store: SQLiteStore) -> TestClient:
    server.store = store
    manager = PluginManager()
    manager.discover_plugins()
    server.plugin_manager = manager
    return TestClient(server.app)


def test_collection_schedule_store_create_update_list_get() -> None:
    store = _make_registered_store()

    created = store.create_or_update_collection_schedule(
        schedule_id="dcp:monitor_daily",
        plugin_id="dcp",
        profile="monitor_daily",
        schedule_cron="0 8,18 * * *",
        timezone="Asia/Shanghai",
        default_request={
            "plugin_id": "dcp",
            "profile": "monitor_daily",
            "dataset_keys": ["daily_meeting"],
            "processing_mode": "async",
            "recent_days": 3,
        },
        enabled=False,
        next_run_at="2026-05-07T08:00:00+08:00",
    )

    assert created["schedule_id"] == "dcp:monitor_daily"
    assert created["default_request"]["dataset_keys"] == ["daily_meeting"]
    assert store.get_collection_schedule("dcp:monitor_daily")["profile"] == "monitor_daily"
    assert len(store.list_collection_schedules(plugin_id="dcp", limit=10)) >= 1


def test_collection_schedule_enable_disable_and_mark_triggered() -> None:
    store = _make_registered_store()
    store.create_or_update_collection_schedule(
        schedule_id="dcp:planning_snapshot",
        plugin_id="dcp",
        profile="planning_snapshot",
        schedule_cron="0 7 * * *",
        timezone="Asia/Shanghai",
        default_request={
            "plugin_id": "dcp",
            "profile": "planning_snapshot",
            "dataset_keys": ["year_progress"],
            "processing_mode": "none",
        },
        enabled=False,
        next_run_at="2026-05-08T07:00:00+08:00",
    )

    store.update_collection_schedule_enabled(
        "dcp:planning_snapshot",
        True,
        next_run_at="2026-05-07T07:00:00+08:00",
    )
    enabled = store.get_collection_schedule("dcp:planning_snapshot")
    assert enabled["enabled"] is True
    assert enabled["next_run_at"] == "2026-05-07T07:00:00+08:00"

    store.mark_collection_schedule_triggered(
        "dcp:planning_snapshot",
        job_id="collect_123",
        next_run_at="2026-05-08T07:00:00+08:00",
    )
    triggered = store.get_collection_schedule("dcp:planning_snapshot")
    assert triggered["last_job_id"] == "collect_123"
    assert triggered["next_run_at"] == "2026-05-08T07:00:00+08:00"
    assert triggered["last_triggered_at"] is not None

    store.update_collection_schedule_enabled("dcp:planning_snapshot", False)
    assert store.get_collection_schedule("dcp:planning_snapshot")["enabled"] is False


def test_get_collection_schedules_api_returns_default_profiles() -> None:
    store = _make_registered_store()
    client = _client(store)

    response = client.get("/collection/v1/schedules")

    assert response.status_code == 200
    profiles = {item["profile"] for item in response.json()["schedules"]}
    assert {"monitor_daily", "spatial_snapshot", "planning_snapshot"}.issubset(profiles)


def test_enable_and_disable_collection_schedule_api() -> None:
    store = _make_registered_store()
    client = _client(store)
    client.get("/collection/v1/schedules")

    enable = client.post("/collection/v1/schedules/dcp:monitor_daily/enable")
    assert enable.status_code == 200
    assert enable.json()["enabled"] is True

    disable = client.post("/collection/v1/schedules/dcp:monitor_daily/disable")
    assert disable.status_code == 200
    assert disable.json()["enabled"] is False


def test_enable_schedule_returns_404_when_missing() -> None:
    store = _make_registered_store()
    client = _client(store)

    response = client.post("/collection/v1/schedules/dcp:missing/enable")

    assert response.status_code == 404


def test_scheduler_tick_creates_job_for_due_schedule(monkeypatch) -> None:
    store = _make_registered_store()
    _client(store)
    server._sync_default_collection_schedules("dcp")
    schedule = store.get_collection_schedule("dcp:monitor_daily")
    store.update_collection_schedule_enabled(
        schedule["schedule_id"],
        True,
        next_run_at="2026-05-07T07:00:00+08:00",
    )
    started: list[tuple[str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        server,
        "_start_external_collection_job",
        lambda job_id, command, cwd: started.append((job_id, tuple(command))),
    )

    result = server.collection_scheduler_tick_once(
        now=datetime.fromisoformat("2026-05-07T08:00:00+08:00")
    )

    assert len(result["triggered"]) == 1
    assert len(result["created_job_ids"]) == 1
    assert started[0][1][4] == "app.commands.dcp_datahub"
    jobs = store.list_external_collection_jobs(plugin_id="dcp", limit=10)
    assert jobs[0]["profile"] == "monitor_daily"
    updated_schedule = store.get_collection_schedule("dcp:monitor_daily")
    assert updated_schedule["last_job_id"] == result["created_job_ids"][0]
    assert updated_schedule["next_run_at"] > "2026-05-07T08:00:00+08:00"


def test_scheduler_tick_skips_disabled_schedule(monkeypatch) -> None:
    store = _make_registered_store()
    _client(store)
    server._sync_default_collection_schedules("dcp")
    monkeypatch.setattr(
        server,
        "_start_external_collection_job",
        lambda job_id, command, cwd: (_ for _ in ()).throw(AssertionError("should not start")),
    )

    result = server.collection_scheduler_tick_once(
        now=datetime.fromisoformat("2026-05-07T08:00:00+08:00")
    )

    assert result["triggered"] == []


def test_scheduler_tick_skips_overlapping_active_job(monkeypatch) -> None:
    store = _make_registered_store()
    _client(store)
    server._sync_default_collection_schedules("dcp")
    schedule = store.get_collection_schedule("dcp:monitor_daily")
    store.update_collection_schedule_enabled(
        schedule["schedule_id"],
        True,
        next_run_at="2026-05-07T07:00:00+08:00",
    )
    store.create_external_collection_job(
        job_id="collect-active",
        plugin_id="dcp",
        profile="monitor_daily",
        dataset_keys=["daily_meeting"],
        mode="incremental",
        command=["uv", "run", "python", "-m", "app.commands.dcp_datahub"],
        cwd="D:/vibe-coding/vibe-workspace/vibe-downloader/src",
        datahub_url="http://127.0.0.1:8000",
        processing_mode="async",
        recent_days=3,
    )
    monkeypatch.setattr(
        server,
        "_start_external_collection_job",
        lambda job_id, command, cwd: (_ for _ in ()).throw(AssertionError("should not start")),
    )

    result = server.collection_scheduler_tick_once(
        now=datetime.fromisoformat("2026-05-07T08:00:00+08:00")
    )

    assert result["triggered"] == []
    assert result["skipped"][0]["job_id"] == "collect-active"


def test_scheduler_tick_api_returns_triggered_result(monkeypatch) -> None:
    store = _make_registered_store()
    client = _client(store)
    client.get("/collection/v1/schedules")
    store.update_collection_schedule_enabled(
        "dcp:planning_snapshot",
        True,
        next_run_at="2026-05-07T06:00:00+08:00",
    )
    monkeypatch.setattr(
        server,
        "_start_external_collection_job",
        lambda job_id, command, cwd: None,
    )

    response = client.post("/collection/v1/scheduler/tick")

    assert response.status_code == 200
    assert response.json()["created_job_ids"]
