from __future__ import annotations

from pathlib import Path

import yaml

from src.datahub.core.plugin_loader import load_plugin
from src.datahub.core.registry import load_registry_from_plugins


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMANDS = {
    "project_tech_full": {"projectCode"},
    "daily_meeting_today_snapshot": {"date"},
    "daily_meeting_yesterday_final": {"date"},
    "plan_professional_all": {"planYear"},
    "year_progress_project_domain": {"year"},
    "safety_daily_meeting_range": {"startDate", "endDate"},
}


def main() -> None:
    plugin_dir = ROOT / "plugins" / "dcp"
    plugin = load_plugin(plugin_dir)
    registry = load_registry_from_plugins([plugin])
    assert plugin.connector.type == "downloader_sync"
    commands = {cmd.job_type: set(cmd.required_params) for cmd in plugin.commands}
    assert commands == EXPECTED_COMMANDS

    tables = registry.tables
    assert len(tables) == 15
    assert tables["dcp_year_progress_project_domain"].write_mode == "replace_scope"
    assert tables["dcp_safety_daily_meeting"].write_mode == "upsert"
    assert all(route.table in tables for route in plugin.query_routes)
    assert len(plugin.query_routes) == 15

    raw_tables = yaml.safe_load((plugin_dir / "tables.yaml").read_text(encoding="utf-8"))["tables"]
    assert "extra" in raw_tables["dcp_plan_progress_management"]["columns"]
    assert "raw" not in raw_tables["dcp_safety_daily_meeting"]["columns"]

    forbidden = ["dcp_sdk", "DcpApiClient", "cookie", "session", "瑞数", "pageName", "apiName"]
    for path in plugin_dir.glob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in text, f"{needle} leaked into {path}"
    print("phase2 ok")


if __name__ == "__main__":
    main()
