from __future__ import annotations

from typing import Any


def normalize_tower_no(value: Any) -> str | None:
    if value in (None, ""):
        return None
    normalized = str(value).strip()
    return normalized or None


def dcp_tower_key(single_project_code: str, bidding_section_code: str, tower_no: str) -> str:
    return f"dcp:tower:{single_project_code}:{bidding_section_code}:{tower_no}"


def dcp_unscoped_tower_key(tower_no: str) -> str:
    return f"dcp:tower:{tower_no}"
