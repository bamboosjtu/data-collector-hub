from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

logger = logging.getLogger(__name__)

# Sentinel indicating no explicit key was configured — dev mode will use a default.
_UNCONFIGURED = "DATAHUB_CALLBACK_API_KEY_NOT_SET"


@dataclass(frozen=True)
class Settings:
    db_path: Path = ROOT / "data" / "datahub_mvp.db"
    plugin_dir: Path = ROOT / "plugins"
    callback_base_url: str = "http://localhost:8000"
    callback_api_key: str = _UNCONFIGURED
    dev_mode: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        raw_key = os.getenv("DATAHUB_CALLBACK_API_KEY", _UNCONFIGURED)
        dev_mode = os.getenv("DATAHUB_DEV_MODE", "1").strip() in ("1", "true", "yes")

        # In dev mode, fall back to a known dev key if none configured.
        # In production mode, a missing key is a startup error.
        if raw_key == _UNCONFIGURED:
            if dev_mode:
                raw_key = "dev-ingestion-key"
                logger.warning("DATAHUB_CALLBACK_API_KEY not set; using dev default in dev mode")
            else:
                raise RuntimeError(
                    "DATAHUB_CALLBACK_API_KEY must be explicitly set in production "
                    "(set DATAHUB_DEV_MODE=1 for development defaults)"
                )

        return cls(
            db_path=Path(os.getenv("DATAHUB_DB_PATH", str(cls.db_path))),
            plugin_dir=Path(os.getenv("DATAHUB_PLUGIN_DIR", str(cls.plugin_dir))),
            callback_base_url=os.getenv("DATAHUB_CALLBACK_BASE_URL", cls.callback_base_url).rstrip("/"),
            callback_api_key=raw_key,
            dev_mode=dev_mode,
        )
