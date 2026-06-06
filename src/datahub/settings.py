from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    db_path: Path = ROOT / "data" / "datahub_mvp.db"
    plugin_dir: Path = ROOT / "plugins"
    callback_base_url: str = "http://localhost:8000"
    callback_api_key: str = os.getenv("DATAHUB_CALLBACK_API_KEY", "dev-ingestion-key")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=Path(os.getenv("DATAHUB_DB_PATH", str(cls.db_path))),
            plugin_dir=Path(os.getenv("DATAHUB_PLUGIN_DIR", str(cls.plugin_dir))),
            callback_base_url=os.getenv("DATAHUB_CALLBACK_BASE_URL", cls.callback_base_url).rstrip("/"),
            callback_api_key=os.getenv("DATAHUB_CALLBACK_API_KEY", cls.callback_api_key),
        )
