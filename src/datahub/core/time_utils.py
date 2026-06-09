"""DataHub timezone-aware time utilities.

All business dates and timestamps in DataHub use Asia/Shanghai (Beijing time).
This module provides a single source of truth for timezone-aware time operations.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

DATAHUB_TZ = ZoneInfo("Asia/Shanghai")


def datahub_now() -> datetime:
    """Current datetime in DataHub timezone (Asia/Shanghai)."""
    return datetime.now(DATAHUB_TZ)


def datahub_today() -> date:
    """Current date in DataHub timezone (Asia/Shanghai)."""
    return datahub_now().date()


def datahub_yesterday() -> date:
    """Yesterday's date in DataHub timezone."""
    return datahub_today() - timedelta(days=1)


def datahub_days_ago(n: int) -> date:
    """Date N days ago in DataHub timezone."""
    return datahub_today() - timedelta(days=n)


def datahub_current_year() -> str:
    """Current year as string in DataHub timezone."""
    return str(datahub_today().year)


def datahub_now_text() -> str:
    """Current timestamp as text string for SQLite storage: '%Y-%m-%d %H:%M:%S'."""
    return datahub_now().strftime("%Y-%m-%d %H:%M:%S")
