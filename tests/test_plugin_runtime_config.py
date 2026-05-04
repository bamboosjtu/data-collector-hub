from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

import api.server as server
from core.plugin_config_validator import validate_plugin_runtime_config
from core.plugin_manager import PluginManager
from storage.sqlite_store import SQLiteStore


def _make_registered_store() -> SQLiteStore:
    artifacts_dir = Path(__file__).resolve().parent / ".artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    db_path = artifacts_dir / f"runtime-config-{uuid4().hex}.db"
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


def test_dcp_default_runtime_config_targets_monitor_mvp_datasets():
    store = _make_registered_store()

    runtime = store.get_plugin_runtime_config("dcp")
    config = runtime["config"]

    assert runtime["source"] == "default"
    assert config["enabled_datasets"] == [
        "daily_meeting",
        "tower",
        "station",
    ]
    assert config["monitor_datasets"] == ["daily_meeting", "tower", "station"]
    assert config["datasets"]["daily_meeting"]["enabled"] is True
    assert config["datasets"]["daily_meeting"]["collection"] == "safePages"
    assert config["datasets"]["daily_meeting"]["scope"] == "date_partitioned"
    assert config["datasets"]["daily_meeting"]["page_name"] == "meetingListAdmin"
    assert config["datasets"]["daily_meeting"]["page_aliases"] == ["站班会"]
    assert config["datasets"]["daily_meeting"]["expose_to_monitor"] is True
    assert config["datasets"]["tower"]["enabled"] is True
    assert config["datasets"]["tower"]["collection"] == "projectPages"
    assert config["datasets"]["tower"]["scope"] == "project_single"
    assert config["datasets"]["tower"]["page_name"] == "杆塔信息"
    assert config["datasets"]["tower"]["api_names"] == [
        "tower_single_projects",
        "tower_details",
    ]
    assert config["datasets"]["tower"]["expose_to_monitor"] is True
    assert config["datasets"]["station"]["enabled"] is True
    assert config["datasets"]["station"]["collection"] == "projectPages"
    assert config["datasets"]["station"]["scope"] == "project_single"
    assert config["datasets"]["station"]["page_name"] == "变电站坐标"
    assert config["datasets"]["station"]["api_names"] == [
        "substation_single_projects",
        "substation_coordinates",
    ]
    assert config["datasets"]["station"]["expose_to_monitor"] is True
    assert config["datasets"]["line_section"]["enabled"] is False
    assert config["datasets"]["line_section"]["collection"] == "projectPages"
    assert config["datasets"]["line_section"]["scope"] == "project_single"
    assert config["datasets"]["line_section"]["page_name"] == "区段划分"
    assert config["datasets"]["line_section"]["api_names"] == [
        "section_single_projects",
        "section_details",
    ]
    assert config["datasets"]["line_section"]["expose_to_monitor"] is False
    assert config["datasets"]["year_progress"]["enabled"] is False
    assert config["datasets"]["year_progress"]["collection"] == "planPages"
    assert config["datasets"]["year_progress"]["scope"] == "snapshot"
    assert config["datasets"]["year_progress"]["page_name"] == "年度进度计划分析"
    assert config["datasets"]["year_progress"]["expose_to_monitor"] is False


def test_old_runtime_config_is_deep_merged_with_schema_defaults():
    store = _make_registered_store()
    old_runtime_config = {
        "collector_type": "external",
        "source_system": "dcp",
        "enabled_datasets": ["daily_meeting", "tower", "station"],
        "datasets": {
            "daily_meeting": {
                "enabled": True,
                "collection": "safePages",
                "scope": "date_partitioned",
                "page_name": "meetingListAdmin",
            },
            "tower": {
                "enabled": True,
                "collection": "projectPages",
                "scope": "project_single",
                "page_name": "杆塔信息",
            },
            "station": {
                "enabled": True,
                "collection": "projectPages",
                "scope": "project_single",
                "page_name": "变电站坐标",
            },
        },
    }
    store.save_plugin_runtime_config("dcp", old_runtime_config)

    runtime = store.get_plugin_runtime_config("dcp")
    config = runtime["config"]

    assert runtime["source"] == "runtime+defaults"
    assert "line_section" in config["datasets"]
    assert "year_progress" in config["datasets"]
    assert config["datasets"]["daily_meeting"]["output_policy"]["partition_by"] == "work_date"
    assert config["datasets"]["daily_meeting"]["page_aliases"] == ["站班会"]
    assert config["downloader_profile"] == "dcp_monitor_mvp"


def test_plugin_runtime_config_survives_plugin_rediscovery_registration():
    store = _make_registered_store()
    store.save_plugin_runtime_config(
        "dcp",
        {
            "schedule_cron": "*/15 * * * *",
            "datasets": {
                "daily_meeting": {
                    "output_policy": {
                        "file_pattern": "custom/{yyyy}-{MM}-{dd}.json",
                    }
                }
            },
        },
    )

    manager = PluginManager()
    manager.discover_plugins()
    manager.save_discovered_plugins(store)

    config = store.get_plugin_runtime_config("dcp")["config"]
    assert config["schedule_cron"] == "*/15 * * * *"
    assert (
        config["datasets"]["daily_meeting"]["output_policy"]["file_pattern"]
        == "custom/{yyyy}-{MM}-{dd}.json"
    )
    assert config["datasets"]["daily_meeting"]["output_policy"]["partition_by"] == "work_date"


def test_put_plugin_config_can_modify_schedule_cron():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={"config": {"schedule_cron": "*/30 * * * *"}},
    )

    assert response.status_code == 200
    assert response.json()["config"]["schedule_cron"] == "*/30 * * * *"
    assert store.get_plugin_runtime_config("dcp")["config"]["schedule_cron"] == "*/30 * * * *"


def test_put_plugin_config_rejects_unknown_enabled_dataset():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={"config": {"enabled_datasets": ["daily_meeting", "unknown_dataset"]}},
    )

    assert response.status_code == 400
    assert "enabled_datasets contains unknown datasets" in str(response.json()["detail"])


def test_put_plugin_config_rejects_monitor_dataset_not_exposed():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={"config": {"monitor_datasets": ["daily_meeting", "line_section"]}},
    )

    assert response.status_code == 400
    assert "not exposed to monitor" in str(response.json()["detail"])


def test_put_plugin_config_rejects_enabled_dataset_marked_disabled():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={
            "config": {
                "enabled_datasets": ["daily_meeting", "tower", "station", "line_section"],
                "datasets": {
                    "line_section": {
                        "enabled": False,
                    }
                }
            }
        },
    )

    assert response.status_code == 400
    assert "enabled_datasets contains disabled dataset: line_section" in str(response.json()["detail"])


def test_put_plugin_config_rejects_invalid_collection():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={
            "config": {
                "datasets": {
                    "tower": {
                        "collection": "badPages",
                    }
                }
            }
        },
    )

    assert response.status_code == 400
    assert "datasets.tower.collection" in str(response.json()["detail"])


def test_put_plugin_config_rejects_invalid_scope():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={
            "config": {
                "datasets": {
                    "tower": {
                        "scope": "bad_scope",
                    }
                }
            }
        },
    )

    assert response.status_code == 400
    assert "datasets.tower.scope" in str(response.json()["detail"])


def test_deep_merge_keeps_nested_output_policy_fields():
    store = _make_registered_store()
    client = _client(store)

    response = client.put(
        "/api/plugins/dcp/config",
        json={
            "config": {
                "datasets": {
                    "daily_meeting": {
                        "output_policy": {
                            "file_pattern": "daily_meeting/{yyyy}/{MM}/{dd}.json",
                        }
                    }
                }
            }
        },
    )

    assert response.status_code == 200
    output_policy = response.json()["config"]["datasets"]["daily_meeting"]["output_policy"]
    assert output_policy["file_pattern"] == "daily_meeting/{yyyy}/{MM}/{dd}.json"
    assert output_policy["partition_by"] == "work_date"
    assert output_policy["immutable_before_today"] is True


def test_trigger_dcp_external_plugin_returns_409():
    store = _make_registered_store()
    client = _client(store)
    server.plugin_manager._metadata_cache["dcp"].tags = []

    response = client.post("/api/plugins/dcp/trigger", json={"config": {}})

    assert response.status_code == 409
    assert "external" in response.json()["detail"]


def test_validator_rejects_invalid_dcp_runtime_config():
    store = _make_registered_store()
    config = store.get_plugin_runtime_config("dcp")["config"]
    config["monitor_datasets"] = ["missing_dataset"]

    errors = validate_plugin_runtime_config("dcp", config)

    assert any("monitor_datasets contains unknown datasets" in error for error in errors)


def test_validator_rejects_nested_plaintext_secret():
    store = _make_registered_store()
    config = store.get_plugin_runtime_config("dcp")["config"]
    config["datasets"]["tower"]["credentials"] = {"password": "plain-text"}

    errors = validate_plugin_runtime_config("dcp", config)

    assert any("datasets.tower.credentials.password" in error for error in errors)


def test_get_plugin_config_returns_config_and_schema():
    store = _make_registered_store()
    client = _client(store)

    response = client.get("/api/plugins/dcp/config")

    assert response.status_code == 200
    body = response.json()
    assert body["plugin_id"] == "dcp"
    assert body["config"]["source_system"] == "dcp"
    assert body["config"]["downloader_profile"] == "dcp_monitor_mvp"
    assert body["config"]["monitor_datasets"] == ["daily_meeting", "tower", "station"]
    assert body["config"]["datasets"]["line_section"]["page_name"] == "区段划分"
    assert "enabled_datasets" in body["config_schema"]
    assert "datasets" in body["config_schema"]


def test_api_plugins_returns_dcp_plugin_kind_and_execution_mode():
    store = _make_registered_store()
    client = _client(store)

    response = client.get("/api/plugins")

    assert response.status_code == 200
    plugins = {plugin["id"]: plugin for plugin in response.json()["plugins"]}
    assert plugins["dcp"]["plugin_kind"] == "external"
    assert plugins["dcp"]["execution_mode"] == "external_job"
