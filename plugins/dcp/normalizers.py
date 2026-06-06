"""DCP plugin normalizers.

Each normalizer handler takes (table_name, scope_values, rows) and returns
a list of {"table_name": ..., "scope_values": ..., "rows": ...} dicts.
"""

from __future__ import annotations

from typing import Any

# Fields to exclude from all normalizer outputs (DCP system fields)
_SKIP_FIELDS = {"extra", "traceId", "children", "singleList", "raw", "recordKey", "sourceRowIndex"}

# Fields specific to each progress type level
_PROJECT_PROGRESS_FIELDS = {
    "id", "prjCode", "prjName", "provinceCode", "buildUnitCode",
    "provinceBuildUnitName", "projectType", "weight",
    "constructionStatus", "constructionLineLength", "constrTransformerCapacity",
    "progressStatus", "planProgress", "actualProgress", "prjActualProgress",
    "weeklyIncrease", "monthlyIncrease", "noUpdateDays", "planDuration",
    "planStartDate", "planFinDate", "actualDuration", "actualStartDate",
    "actualFinDate", "rectifyFlag", "stopFlag", "warningFlag",
    "suspensionCause", "suspensionCauseType", "updateTime", "orderNum", "messageId",
}

_SINGLE_PROJECT_PROGRESS_FIELDS = _PROJECT_PROGRESS_FIELDS | {
    "singleProjectCode", "singleActualProgress", "singleProjectDetailsType",
}

_BIDDING_SECTION_PROGRESS_FIELDS = _SINGLE_PROJECT_PROGRESS_FIELDS | {
    "biddingSectionCode", "biddingSectionType",
}


def normalize_plan_sgcc_year(
    table_name: str,
    scope_values: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expand dcp_plan_sgcc_year raw rows into dcp_plan_projects and dcp_plan_single_projects."""
    project_rows: list[dict[str, Any]] = []
    single_project_rows: list[dict[str, Any]] = []

    for row in rows:
        raw = row.get("raw") or {}
        year = row.get("year") or scope_values.get("year", "")

        # Project-level row
        proj = {"year": year}
        for k, v in raw.items():
            if k not in _SKIP_FIELDS:
                proj[k] = v
        project_rows.append(proj)

        # Single project rows from singleList
        for item in raw.get("singleList") or []:
            sp = {"year": year}
            for k, v in item.items():
                if k not in _SKIP_FIELDS:
                    sp[k] = v
            single_project_rows.append(sp)

    return [
        {"table_name": "dcp_plan_projects", "scope_values": scope_values, "rows": project_rows},
        {"table_name": "dcp_plan_single_projects", "scope_values": scope_values, "rows": single_project_rows},
    ]


def normalize_plan_progress(
    table_name: str,
    scope_values: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expand dcp_plan_progress raw rows into three progress tables.

    The raw data has a tree structure:
      - type=1: project-level progress (primary key: prjCode)
      - type=2: single-project-level progress (primary key: singleProjectCode)
      - type=3: bidding-section-level progress (primary key: biddingSectionCode)
    """
    project_progress: list[dict[str, Any]] = []
    single_project_progress: list[dict[str, Any]] = []
    bidding_section_progress: list[dict[str, Any]] = []

    def _extract_row(raw: dict[str, Any], allowed_fields: set[str]) -> dict[str, Any]:
        """Extract business fields from a raw progress record, filtering by allowed fields."""
        result = {}
        for k, v in raw.items():
            if k not in _SKIP_FIELDS and k in allowed_fields:
                result[k] = v
        return result

    def _flatten(raw_list: list[dict[str, Any]]) -> None:
        for raw in raw_list:
            row_type = raw.get("type")

            if row_type == 1:
                project_progress.append(_extract_row(raw, _PROJECT_PROGRESS_FIELDS))
            elif row_type == 2:
                single_project_progress.append(_extract_row(raw, _SINGLE_PROJECT_PROGRESS_FIELDS))
            elif row_type == 3:
                bidding_section_progress.append(_extract_row(raw, _BIDDING_SECTION_PROGRESS_FIELDS))

            for child in raw.get("children") or []:
                _flatten([child])

    for row in rows:
        raw = row.get("raw") or {}
        _flatten([raw])

    return [
        {"table_name": "dcp_plan_project_progress", "scope_values": scope_values, "rows": project_progress},
        {"table_name": "dcp_plan_single_project_progress", "scope_values": scope_values, "rows": single_project_progress},
        {"table_name": "dcp_plan_bidding_section_progress", "scope_values": scope_values, "rows": bidding_section_progress},
    ]


def normalize_plan_dept_key_personnel(
    table_name: str,
    scope_values: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expand dcp_plan_dept_key_personnel raw rows into field-extracted business table."""
    personnel_rows: list[dict[str, Any]] = []

    for row in rows:
        raw = row.get("raw") or {}
        extracted = {}
        for k, v in raw.items():
            if k not in _SKIP_FIELDS:
                extracted[k] = v
        personnel_rows.append(extracted)

    return [
        {"table_name": "dcp_plan_dept_key_personnel", "scope_values": scope_values, "rows": personnel_rows},
    ]


# Fields allowed in dcp_line_sections (from sectionDTOList)
_SECTION_DTO_FIELDS = {
    "id", "biddingSectionCode", "sectionNo", "sectionName",
    "startNo", "terminalNo", "sectionLength", "towerTotalNumber",
    "totalTensionTower", "sequenceNo", "provinceCode",
    "frontSpan", "backSpan", "strartAdjustType", "startDistance",
    "endAdjustType", "endDistance",
}


def normalize_line_section(
    table_name: str,
    scope_values: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expand dcp_line_section two-layer structure into dcp_line_branches and dcp_line_sections.

    Outer layer (branch): sectionId, sectionName, sectionVo
    Inner layer (sections): sectionVo.sectionDTOList
    """
    branch_rows: list[dict[str, Any]] = []
    section_rows: list[dict[str, Any]] = []

    for row in rows:
        bidding_section_code = row.get("biddingSectionCode") or scope_values.get("biddingSectionCode", "")
        section_id = row.get("sectionId", "")
        section_name = row.get("sectionName", "")
        section_vo = row.get("sectionVo") or {}

        # Branch row (outer layer)
        branch_rows.append({
            "biddingSectionCode": bidding_section_code,
            "branchId": section_id,
            "branchName": section_name,
            "towerNoList": section_vo.get("towerNoList"),
            "spanList": section_vo.get("spanList"),
        })

        # Section rows (inner layer from sectionDTOList)
        for dto in section_vo.get("sectionDTOList") or []:
            section_row = {"biddingSectionCode": bidding_section_code, "branchId": section_id}
            for k, v in dto.items():
                if k in _SECTION_DTO_FIELDS:
                    # Map id -> sectionId for the target table
                    if k == "id":
                        section_row["sectionId"] = v
                    else:
                        section_row[k] = v
            section_rows.append(section_row)

    return [
        {"table_name": "dcp_line_branches", "scope_values": scope_values, "rows": branch_rows},
        {"table_name": "dcp_line_sections", "scope_values": scope_values, "rows": section_rows},
    ]
