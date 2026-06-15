"""Check ENV configuration completeness for DataHub MVP deployment."""

import os
import sys

DEFAULT_DB_PATH = "data/datahub.db"
DEFAULT_CALLBACK_BASE_URL = "http://localhost:8000"


def _ok(msg: str) -> None:
    print(f"[OK]   {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def check_required() -> bool:
    """Return True if all required checks pass."""
    all_ok = True

    # DATAHUB_DB_PATH
    db_path = os.getenv("DATAHUB_DB_PATH", DEFAULT_DB_PATH)
    parent = os.path.dirname(db_path)
    if parent:
        if os.path.isdir(parent):
            _ok(f"DATAHUB_DB_PATH={db_path} (parent directory exists)")
        elif os.path.isdir(os.path.dirname(parent)):
            _ok(f"DATAHUB_DB_PATH={db_path} (parent directory creatable)")
        else:
            _fail(f"DATAHUB_DB_PATH={db_path} (parent directory does not exist and cannot be created)")
            all_ok = False
    else:
        _ok(f"DATAHUB_DB_PATH={db_path} (current directory)")

    # DATAHUB_CALLBACK_BASE_URL
    base_url = os.getenv("DATAHUB_CALLBACK_BASE_URL", DEFAULT_CALLBACK_BASE_URL)
    if base_url.startswith("http://") or base_url.startswith("https://"):
        _ok(f"DATAHUB_CALLBACK_BASE_URL={base_url}")
    else:
        _fail(f"DATAHUB_CALLBACK_BASE_URL={base_url} (must start with http:// or https://)")
        all_ok = False

    # DATAHUB_CALLBACK_API_KEY
    api_key = os.getenv("DATAHUB_CALLBACK_API_KEY")
    dev_mode = os.getenv("DATAHUB_DEV_MODE") == "1"
    if dev_mode:
        if api_key:
            _ok("DATAHUB_CALLBACK_API_KEY is set")
        else:
            _warn("DATAHUB_CALLBACK_API_KEY is not set (dev mode - acceptable for development)")
    else:
        if api_key:
            _ok("DATAHUB_CALLBACK_API_KEY is set")
        else:
            _fail("DATAHUB_CALLBACK_API_KEY is not set (required in production mode)")
            all_ok = False

    # DATAHUB_DEV_MODE
    dev_val = os.getenv("DATAHUB_DEV_MODE", "(not set)")
    _ok(f"DATAHUB_DEV_MODE={dev_val}")

    return all_ok


def check_optional() -> None:
    """Print current values of optional variables."""

    for var in (
        "DATAHUB_COLLECTION_SCHEDULER_ENABLED",
        "DATAHUB_DAILY_DCP_REFRESH_ENABLED",
        "DATAHUB_DAILY_DCP_REFRESH_TIME",
    ):
        _ok(f"{var}={os.getenv(var, '(not set)')}")

    # DATAHUB_DAILY_DCP_RECENT_DAYS – must be a positive integer if set
    recent_days = os.getenv("DATAHUB_DAILY_DCP_RECENT_DAYS")
    if recent_days is None:
        _ok("DATAHUB_DAILY_DCP_RECENT_DAYS=(not set)")
    elif recent_days.isdigit() and int(recent_days) > 0:
        _ok(f"DATAHUB_DAILY_DCP_RECENT_DAYS={recent_days}")
    else:
        _warn(f"DATAHUB_DAILY_DCP_RECENT_DAYS={recent_days} (expected a positive integer)")

    # DATAHUB_COLLECTION_SCHEDULER_TICK_SECONDS
    tick = os.getenv("DATAHUB_COLLECTION_SCHEDULER_TICK_SECONDS")
    _ok(f"DATAHUB_COLLECTION_SCHEDULER_TICK_SECONDS={tick or '(not set)'}")

    # DATAHUB_PLUGIN_DIR – validate directory exists
    plugin_dir = os.getenv("DATAHUB_PLUGIN_DIR")
    if plugin_dir is None:
        _ok("DATAHUB_PLUGIN_DIR=(not set)")
    elif os.path.isdir(plugin_dir):
        _ok(f"DATAHUB_PLUGIN_DIR={plugin_dir}")
    else:
        _warn(f"DATAHUB_PLUGIN_DIR={plugin_dir} (directory does not exist)")


def main() -> None:
    print("=== DataHub MVP Environment Check ===\n")

    print("--- Required Variables ---")
    required_ok = check_required()

    print("\n--- Optional Variables ---")
    check_optional()

    print()
    if required_ok:
        _ok("All required checks passed")
        sys.exit(0)
    else:
        _fail("One or more required checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
