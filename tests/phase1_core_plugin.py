from __future__ import annotations

import tempfile
from pathlib import Path

from src.datahub.core.plugin_loader import load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.settings import Settings
from src.datahub.app import create_app


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    plugins = load_all_plugins(ROOT / "plugins")
    assert any(plugin.name == "dcp" for plugin in plugins)
    registry = load_registry_from_plugins(plugins)
    assert "dcp_plan_progress_management" in registry.tables
    assert "dcp_safety_daily_meeting" in registry.tables
    assert "plan_professional" in registry.datasets

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        empty_plugins = tmp_path / "plugins"
        empty_plugins.mkdir()
        app = create_app(Settings(db_path=tmp_path / "empty.sqlite", plugin_dir=empty_plugins, callback_base_url="http://datahub.test"))
        assert app.state.registry.tables == {}

    blocked = ["dcp_sdk", "DcpApiClient", "pageName", "apiName", "瑞数"]
    for path in (ROOT / "src" / "datahub" / "core").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for needle in blocked:
            assert needle not in text, f"{needle} leaked into {path}"
    print("phase1 ok")


if __name__ == "__main__":
    main()
