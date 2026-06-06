"""DCP plugin normalizers.

Each normalizer handler takes (table_name, scope_values, rows) and returns
a list of {"table_name": ..., "scope_values": ..., "rows": ...} dicts.
"""

from __future__ import annotations

from typing import Any


def normalize_plan_sgcc_year(
    table_name: str,
    scope_values: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expand dcp_plan_sgcc_year raw rows into dcp_projects and dcp_single_projects.

    Input rows come from downloader's RawDcpApiCollectExecutor, each row has:
      - year: scope year (from planner scope_values)
      - recordKey: sha256 hash of the original record
      - raw: the complete original project record from yearPlanView API
      - sourceRowIndex: row index

    The raw record contains:
      - prjCode, prjName, provinceCode, provinceName, buildUnitCode, buildUnitName, ...
      - singleList: list of single project dicts with singleProjectCode, singleProjectName, ...
    """
    project_rows: list[dict[str, Any]] = []
    single_project_rows: list[dict[str, Any]] = []

    for row in rows:
        raw = row.get("raw") or {}
        year = row.get("year") or scope_values.get("year", "")

        # Project-level row
        project_rows.append({
            "year": year,
            "projectCode": raw.get("prjCode"),
            "projectName": raw.get("prjName"),
            "provinceCode": raw.get("provinceCode"),
            "provinceName": raw.get("provinceName"),
            "buildUnitCode": raw.get("buildUnitCode"),
            "buildUnitName": raw.get("buildUnitName"),
            "voltageLevel": raw.get("voltageLevel"),
            "voltageLevelName": raw.get("voltageLevelName"),
            "constrNature": raw.get("constrNature"),
            "constrNatureName": raw.get("constrNatureName"),
            "constructionCategory": raw.get("constructionCategory"),
            "constructionCategoryName": raw.get("constructionCategoryName"),
            "projectType": raw.get("projectType"),
            "planNature": raw.get("planNature"),
            "planNatureName": raw.get("planNatureName"),
            "constructionLineLength": raw.get("constructionLineLength"),
            "constrTransformerCapacity": raw.get("constrTransformerCapacity"),
            "raw": raw,
        })

        # Single project rows from singleList
        for item in raw.get("singleList") or []:
            single_project_rows.append({
                "year": year,
                "projectCode": raw.get("prjCode"),
                "projectName": raw.get("prjName"),
                "singleProjectCode": item.get("singleProjectCode"),
                "singleProjectName": item.get("singleProjectName"),
                "singleProjectTypeName": item.get("singleProjectTypeName"),
                "raw": item,
            })

    return [
        {"table_name": "dcp_projects", "scope_values": scope_values, "rows": project_rows},
        {"table_name": "dcp_single_projects", "scope_values": scope_values, "rows": single_project_rows},
    ]
