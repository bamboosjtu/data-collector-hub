from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from src.datahub.app import create_app
from src.datahub.settings import Settings
from tests.phase5_api_runtime import request


ROOT = Path(__file__).resolve().parents[1]
CORE_DIRS = [
    ROOT / "src" / "datahub" / "core",
    ROOT / "src" / "datahub" / "ingestion",
    ROOT / "src" / "datahub" / "storage",
    ROOT / "src" / "datahub" / "api",
]
FORBIDDEN_CORE = ["dcp_sdk", "DcpApiClient", "pageName", "apiName", "瑞数"]


def main() -> None:
    for directory in CORE_DIRS:
        for path in directory.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for needle in FORBIDDEN_CORE:
                assert needle not in text, f"{needle} leaked into {path}"

    assert not (ROOT / "api" / "server.py").exists(), "old api.server compatibility path still exists"
    assert not (ROOT / "src" / "datahub" / "downloader.py").exists(), "old downloader module still exists"
    assert not (ROOT / "scripts" / "integration_collect_dcp.py").exists(), "direct DCP integration script still exists"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_root = tmp_path / "plugins"
        demo = plugin_root / "demo"
        demo.mkdir(parents=True)
        (demo / "plugin.yaml").write_text(
            """
name: demo
version: 1
display:
  label: Demo
connector:
  type: downloader_sync
  base_url: http://localhost:8010
commands: []
query_routes:
  - path: /api/v1/demo/items
    table: demo_items
    query_filters:
      scope: scope
""".strip(),
            encoding="utf-8",
        )
        (demo / "tables.yaml").write_text(
            """
version: 1
tables:
  demo_items:
    dataset_key: demo
    description: Demo items
    write_mode: upsert
    scope_column_names: [scope]
    primary_key: [scope, id]
    columns:
      scope: {type: string, nullable: false}
      id: {type: string, nullable: false}
      name: {type: string, nullable: true}
""".strip(),
            encoding="utf-8",
        )
        app = create_app(Settings(db_path=tmp_path / "demo.sqlite", plugin_dir=plugin_root, callback_base_url="http://datahub.test"))
        assert request(app, "GET", "/schemas").json["tables"]["demo_items"]["dataset_key"] == "demo"

    for phase in range(0, 6):
        subprocess.run([sys.executable, str(ROOT / "tests" / f"phase{phase}_{_phase_name(phase)}.py")], cwd=ROOT, check=True)
    print("phase6 ok")


def _phase_name(phase: int) -> str:
    return {
        0: "plan",
        1: "core_plugin",
        2: "dcp_plugin",
        3: "storage",
        4: "ingestion",
        5: "api_runtime",
    }[phase]


if __name__ == "__main__":
    main()
