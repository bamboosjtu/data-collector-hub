"""Schedule API: endpoints for managing collection plans and runs."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.datahub.core.services.collection_plan_service import CollectionPlanError, CollectionPlanService
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope

logger = logging.getLogger(__name__)


def build_schedules_router(
    *,
    store: DataHubStore,
    plan_service: CollectionPlanService,
) -> APIRouter:
    router = APIRouter()

    @router.get("/admin/schedules/plans", dependencies=[Depends(require_scope(store, "admin"))])
    def list_plans() -> dict[str, Any]:
        plans = plan_service.list_plans()
        return {"items": plans}

    @router.get("/admin/schedules/plans/{plan_name}", dependencies=[Depends(require_scope(store, "admin"))])
    def get_plan(plan_name: str) -> dict[str, Any]:
        plan = plan_service.get_plan(plan_name)
        if not plan:
            raise HTTPException(status_code=404, detail=f"plan {plan_name} not found")
        return plan

    @router.post("/admin/schedules/plans/{plan_name}/run", status_code=202, dependencies=[Depends(require_scope(store, "admin"))])
    def run_plan_now(plan_name: str) -> dict[str, Any]:
        try:
            result = plan_service.run_plan_now(plan_name, source="api")
        except CollectionPlanError as exc:
            status_code = 409 if exc.error_code == "plan_already_running" else 422
            if exc.error_code == "plan_not_found":
                status_code = 404
            raise HTTPException(status_code=status_code, detail={"error": exc.error_code, "message": exc.message}) from exc
        return {
            "run_id": result.run_id,
            "status": result.status,
        }

    @router.get("/admin/schedules/runs", dependencies=[Depends(require_scope(store, "admin"))])
    def list_runs(plan_name: str | None = None, limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        runs = plan_service.list_runs(plan_name, limit)
        return {"items": runs}

    @router.get("/admin/schedules/runs/{run_id}", dependencies=[Depends(require_scope(store, "admin"))])
    def get_run(run_id: str) -> dict[str, Any]:
        run = plan_service.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"run {run_id} not found")
        steps = plan_service._store.get_scheduled_run_steps(run_id)
        return {**run, "steps": steps}

    return router
