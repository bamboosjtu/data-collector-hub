"""Collection plan service: manages scheduled plans, runs, and step execution.

All command triggering goes through JobService.submit_command().
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from src.datahub.core.services.job_service import JobService, JobServiceError
from src.datahub.core.time_utils import datahub_now, datahub_now_text, datahub_today
from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = frozenset({"succeeded", "partial", "failed", "cancelled"})

# Default daily_dcp_refresh plan steps
DAILY_DCP_REFRESH_STEPS = [
    {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_plan_progress", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_dept_key_personnel", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_towers_for_current_plan_projects", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_substations_for_current_plan_projects", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_line_sections_for_current_plan_projects", "params": {}, "wait_for_terminal": True},
    {"command": "backfill_daily_meetings_by_range", "params": {}, "wait_for_terminal": True},
]


class CollectionPlanError(Exception):
    """Raised when a collection plan operation fails."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


@dataclass
class PlanRunResult:
    """Result of a plan run."""
    run_id: str
    status: str
    steps: list[dict[str, Any]]
    error: str | None = None


class CollectionPlanService:
    """Service for managing and executing collection plans."""

    def __init__(
        self,
        *,
        store: DataHubStore,
        job_service: JobService,
        recent_days: int = 3,
    ):
        self._store = store
        self._job_service = job_service
        self._recent_days = recent_days

    def seed_default_plans(self) -> None:
        """Seed the built-in daily_dcp_refresh plan if not exists."""
        existing = self._store.get_scheduled_plan("daily_dcp_refresh")
        if existing:
            return
        config = {
            "steps": DAILY_DCP_REFRESH_STEPS,
            "recent_days": self._recent_days,
        }
        self._store.upsert_scheduled_plan(
            plan_name="daily_dcp_refresh",
            enabled=0,
            schedule_type="daily",
            schedule_time="02:00",
            timezone="Asia/Shanghai",
            config_json=json.dumps(config, ensure_ascii=False),
        )
        logger.info("seeded default plan: daily_dcp_refresh (disabled)")

    def get_plan(self, plan_name: str) -> dict[str, Any] | None:
        return self._store.get_scheduled_plan(plan_name)

    def list_plans(self) -> list[dict[str, Any]]:
        return self._store.list_scheduled_plans()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self._store.get_scheduled_run(run_id)

    def list_runs(self, plan_name: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self._store.list_scheduled_runs(plan_name, limit)

    def run_plan_now(self, plan_name: str, source: str = "api") -> PlanRunResult:
        """Execute a plan immediately. Blocks until all steps complete or a step fails.

        Args:
            plan_name: The plan to execute.
            source: Trigger source — api / cli / scheduler.

        Returns:
            PlanRunResult with run_id, final status, and step details.

        Raises:
            CollectionPlanError: If plan not found or already running.
        """
        plan = self._store.get_scheduled_plan(plan_name)
        if not plan:
            raise CollectionPlanError("plan_not_found", f"plan {plan_name} not found")

        # Prevent overlapping runs
        existing_run = self._store.get_running_plan_run(plan_name)
        if existing_run:
            raise CollectionPlanError(
                "plan_already_running",
                f"plan {plan_name} already has a running run: {existing_run['run_id']}",
            )

        config = json.loads(plan["config_json"] or "{}")
        steps = config.get("steps", [])
        if not steps:
            raise CollectionPlanError("plan_empty", f"plan {plan_name} has no steps")

        # Create run
        run_id = f"run_{plan_name}_{uuid4().hex[:12]}"
        self._store.create_scheduled_run(
            run_id=run_id,
            plan_name=plan_name,
            trigger_source=source,
            status="running",
        )

        # Create step records
        for idx, step_cfg in enumerate(steps):
            params = step_cfg.get("params", {})
            # Dynamic params for backfill_daily_meetings_by_range
            if step_cfg["command"] == "backfill_daily_meetings_by_range":
                recent_days = config.get("recent_days", self._recent_days)
                today = datahub_today()
                start_date = today - timedelta(days=recent_days)
                params = {
                    "startDate": start_date.isoformat(),
                    "endDate": today.isoformat(),
                    "chunk_days": 1,
                }
            self._store.create_scheduled_run_step(
                run_id=run_id,
                step_order=idx,
                command_name=step_cfg["command"],
                params_json=json.dumps(params, ensure_ascii=False),
                status="pending",
                wait_for_terminal=1 if step_cfg.get("wait_for_terminal", True) else 0,
            )

        # Execute steps sequentially
        run_status = "succeeded"
        run_error = None
        step_results = []

        step_rows = self._store.get_scheduled_run_steps(run_id)
        for step_row in step_rows:
            step_id = step_row["id"]
            command_name = step_row["command_name"]
            params = json.loads(step_row["params_json"] or "{}")
            wait_for_terminal = bool(step_row["wait_for_terminal"])

            # Mark step running
            self._store.update_scheduled_run_step(step_id, status="running")

            try:
                job_result = self._job_service.submit_command(
                    command_name, params, source=source,
                )
                self._store.update_scheduled_run_step(
                    step_id, job_id=job_result.ingestion_job_id,
                )
            except JobServiceError as exc:
                self._store.update_scheduled_run_step(
                    step_id, status="failed", error=exc.message,
                )
                run_status = "failed"
                run_error = f"step {command_name} failed: {exc.message}"
                step_results.append({"command": command_name, "status": "failed", "error": exc.message})
                break

            # Wait for terminal status if required
            if wait_for_terminal:
                step_status = self._wait_for_job_terminal(job_result.ingestion_job_id)
                job_detail = self._store.get_job(job_result.ingestion_job_id)
                step_error = job_detail.get("error") if job_detail else None
                self._store.update_scheduled_run_step(
                    step_id, status=step_status, error=step_error,
                    result_json=self._store._json(job_detail) if job_detail else None,
                )
                step_results.append({"command": command_name, "status": step_status, "job_id": job_result.ingestion_job_id})

                if step_status == "failed":
                    run_status = "failed"
                    run_error = f"step {command_name} failed"
                    break
                elif step_status == "partial":
                    if run_status == "succeeded":
                        run_status = "partial"
            else:
                # Fire-and-forget: mark succeeded once submitted
                self._store.update_scheduled_run_step(step_id, status="succeeded")
                step_results.append({"command": command_name, "status": "submitted", "job_id": job_result.ingestion_job_id})

        # Compute next_run_at for daily plans
        next_run_at = None
        if plan["schedule_type"] == "daily" and plan["schedule_time"]:
            tz = ZoneInfo(plan.get("timezone", "Asia/Shanghai"))
            now_tz = datahub_now().astimezone(tz)
            hour, minute = (int(x) for x in plan["schedule_time"].split(":"))
            next_dt = now_tz.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)
            next_run_at = next_dt.strftime("%Y-%m-%d %H:%M:%S")

        # Finalize run
        self._store.update_scheduled_run(run_id, status=run_status, error=run_error)
        self._store.update_plan_last_run(plan_name, run_id=run_id, status=run_status, next_run_at=next_run_at)

        logger.info("plan %s run %s completed: %s", plan_name, run_id, run_status)
        return PlanRunResult(run_id=run_id, status=run_status, steps=step_results, error=run_error)

    def scheduler_tick(self) -> None:
        """Check enabled plans and trigger runs that are due.

        Called periodically by the collection scheduler background thread.
        """
        plans = self._store.list_scheduled_plans()
        now_text = datahub_now_text()

        for plan in plans:
            if not plan["enabled"]:
                continue
            if not plan["next_run_at"]:
                continue
            if plan["next_run_at"] > now_text:
                continue

            # Check for overlapping run
            existing = self._store.get_running_plan_run(plan["plan_name"])
            if existing:
                logger.debug("scheduler: plan %s already running (%s), skipping", plan["plan_name"], existing["run_id"])
                continue

            try:
                logger.info("scheduler: triggering plan %s (scheduled at %s)", plan["plan_name"], plan["next_run_at"])
                self.run_plan_now(plan["plan_name"], source="scheduler")
            except CollectionPlanError as exc:
                logger.error("scheduler: plan %s tick failed: %s", plan["plan_name"], exc.message)
            except Exception as exc:
                logger.error("scheduler: plan %s tick error: %s", plan["plan_name"], exc, exc_info=True)

    def _wait_for_job_terminal(self, ingestion_job_id: str, timeout: float = 3600, poll_interval: float = 5.0) -> str:
        """Poll until an ingestion_job reaches terminal status."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            job = self._store.get_job(ingestion_job_id)
            if job and job["status"] in _TERMINAL_STATUSES:
                return job["status"]
            time.sleep(poll_interval)
        return "failed"

    def mark_stale_runs(self, stale_seconds: int = 7200) -> int:
        """Mark running scheduled_runs as failed if they've been running too long.

        This handles crash recovery: if the process restarts with stale running runs,
        they get marked as failed so new runs can be triggered.
        """
        from src.datahub.core.time_utils import datahub_now
        cutoff = (datahub_now() - timedelta(seconds=stale_seconds)).strftime("%Y-%m-%d %H:%M:%S")
        runs = self._store.list_scheduled_runs(limit=200)
        marked = 0
        for run in runs:
            if run["status"] != "running":
                continue
            if run["started_at"] and run["started_at"] < cutoff:
                self._store.update_scheduled_run(run["run_id"], status="failed", error="stale run marked failed on restart")
                marked += 1
        if marked:
            logger.info("marked %d stale scheduled_runs as failed", marked)
        return marked
