"""Collection plan service: manages scheduled plans, runs, and step execution.

All command triggering goes through JobService.submit_command().
run_plan_now is async: it creates the run and kicks off a background thread,
then returns immediately with status="running".
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from src.datahub.core.services.job_service import JobService, JobServiceError
from src.datahub.core.time_utils import datahub_now, datahub_now_text, datahub_today, datahub_yesterday
from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = frozenset({"succeeded", "partial", "failed", "cancelled"})

# ---------------------------------------------------------------------------
# Dynamic parameter resolver
# ---------------------------------------------------------------------------

# Placeholders that get resolved at plan-run time
_DOLLAR_PLACEHOLDERS = {
    "$today": lambda: datahub_today().isoformat(),
    "$yesterday": lambda: datahub_yesterday().isoformat(),
    "$current_year": lambda: str(datahub_today().year),
}


def resolve_plan_params(params: Any) -> Any:
    """Recursively resolve $-placeholders in plan step params.

    Supported placeholders:
    - "$today" -> e.g. "2026-06-15"
    - "$yesterday" -> e.g. "2026-06-14"
    - "$current_year" -> e.g. "2026"

    Only string values matching a placeholder are replaced.
    Lists and dicts are traversed recursively.
    """
    if isinstance(params, str):
        resolver = _DOLLAR_PLACEHOLDERS.get(params)
        if resolver:
            return resolver()
        return params
    if isinstance(params, list):
        return [resolve_plan_params(item) for item in params]
    if isinstance(params, dict):
        return {k: resolve_plan_params(v) for k, v in params.items()}
    return params


# ---------------------------------------------------------------------------
# Default plan configs
# ---------------------------------------------------------------------------

DCP_INITIAL_FULL_LOAD_CONFIG = {
    "description": "DCP 初始化全量采集",
    "wait_timeout_seconds": 28800,
    "poll_interval_seconds": 5,
    "steps": [
        {"command": "refresh_annual_plans_history", "params": {}, "wait_for_terminal": True},
        {"command": "refresh_plan_progress", "params": {}, "wait_for_terminal": True},
        {"command": "refresh_dept_key_personnel", "params": {}, "wait_for_terminal": True},
        {"command": "refresh_towers_for_all_plan_projects", "params": {"years": [2024, 2025, 2026], "max_concurrency": 5}, "wait_for_terminal": True},
        {"command": "refresh_substations_for_all_plan_projects", "params": {"years": [2024, 2025, 2026], "max_concurrency": 5}, "wait_for_terminal": True},
        {"command": "refresh_line_sections_for_all_plan_projects", "params": {"years": [2024, 2025, 2026], "max_concurrency": 5}, "wait_for_terminal": True},
        {"command": "backfill_daily_meetings_by_range", "params": {"startDate": "2024-01-01", "endDate": "$yesterday", "chunk_days": 1, "max_concurrency": 5}, "wait_for_terminal": True},
    ],
}

DCP_DAILY_UPDATE_CONFIG = {
    "description": "DCP 每日增量更新",
    "wait_timeout_seconds": 7200,
    "poll_interval_seconds": 5,
    "steps": [
        {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
        {"command": "refresh_plan_progress", "params": {}, "wait_for_terminal": True},
        {"command": "refresh_dept_key_personnel", "params": {}, "wait_for_terminal": True},
        {"command": "refresh_towers_for_current_plan_projects", "params": {"max_concurrency": 5}, "wait_for_terminal": True},
        {"command": "refresh_substations_for_current_plan_projects", "params": {"max_concurrency": 5}, "wait_for_terminal": True},
        {"command": "refresh_line_sections_for_current_plan_projects", "params": {"max_concurrency": 5}, "wait_for_terminal": True},
        {"command": "backfill_daily_meetings_by_range", "params": {"startDate": "$today", "endDate": "$today", "chunk_days": 1, "max_concurrency": 5}, "wait_for_terminal": True},
    ],
}

# Legacy plan steps (kept for backward compat with existing DB records)
DAILY_DCP_REFRESH_STEPS = [
    {"command": "refresh_annual_plans_current", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_plan_progress", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_dept_key_personnel", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_towers_for_current_plan_projects", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_substations_for_current_plan_projects", "params": {}, "wait_for_terminal": True},
    {"command": "refresh_line_sections_for_current_plan_projects", "params": {}, "wait_for_terminal": True},
    {"command": "backfill_daily_meetings_by_range", "params": {"startDate": "$today", "endDate": "$today", "chunk_days": 1}, "wait_for_terminal": True},
]


class CollectionPlanError(Exception):
    """Raised when a collection plan operation fails."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


@dataclass
class StartPlanRunResult:
    """Result of starting a plan run (returned immediately, before execution)."""
    run_id: str
    status: str  # always "running" at this point


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

    # ── Plan CRUD ────────────────────────────────────────────────

    def seed_default_plans(self) -> None:
        """Seed the built-in collection plans if they don't exist.

        Creates:
        - dcp_initial_full_load: manual, disabled
        - dcp_daily_update: daily 02:00, disabled
        - daily_dcp_refresh: legacy, kept if already exists
        """
        # Seed dcp_initial_full_load
        if not self._store.get_scheduled_plan("dcp_initial_full_load"):
            self._store.upsert_scheduled_plan(
                plan_name="dcp_initial_full_load",
                enabled=0,
                schedule_type="manual",
                schedule_time=None,
                timezone="Asia/Shanghai",
                config_json=json.dumps(DCP_INITIAL_FULL_LOAD_CONFIG, ensure_ascii=False),
            )
            logger.info("seeded default plan: dcp_initial_full_load (disabled, manual)")

        # Seed dcp_daily_update
        if not self._store.get_scheduled_plan("dcp_daily_update"):
            self._store.upsert_scheduled_plan(
                plan_name="dcp_daily_update",
                enabled=0,
                schedule_type="daily",
                schedule_time="02:00",
                timezone="Asia/Shanghai",
                config_json=json.dumps(DCP_DAILY_UPDATE_CONFIG, ensure_ascii=False),
            )
            logger.info("seeded default plan: dcp_daily_update (disabled, daily 02:00)")

        # Seed legacy daily_dcp_refresh if not exists
        if not self._store.get_scheduled_plan("daily_dcp_refresh"):
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
            logger.info("seeded default plan: daily_dcp_refresh (disabled, legacy)")

    def get_plan(self, plan_name: str) -> dict[str, Any] | None:
        return self._store.get_scheduled_plan(plan_name)

    def list_plans(self) -> list[dict[str, Any]]:
        return self._store.list_scheduled_plans()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self._store.get_scheduled_run(run_id)

    def list_runs(self, plan_name: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self._store.list_scheduled_runs(plan_name, limit)

    # ── Run lifecycle ────────────────────────────────────────────

    def run_plan_now(self, plan_name: str, source: str = "api") -> StartPlanRunResult:
        """Start a plan run immediately (async).

        Creates the run record, creates step records, kicks off a background
        thread to execute steps, and returns immediately with status="running".

        Args:
            plan_name: The plan to execute.
            source: Trigger source — api / cli / scheduler / ui_manual.

        Returns:
            StartPlanRunResult with run_id and status="running".

        Raises:
            CollectionPlanError: If plan not found or already running.
        """
        # Clean up stale runs before overlap check
        self.mark_stale_runs()

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

        # Create step records with resolved params
        for idx, step_cfg in enumerate(steps):
            params = resolve_plan_params(step_cfg.get("params", {}))
            self._store.create_scheduled_run_step(
                run_id=run_id,
                step_order=idx,
                command_name=step_cfg["command"],
                params_json=json.dumps(params, ensure_ascii=False),
                status="pending",
                wait_for_terminal=1 if step_cfg.get("wait_for_terminal", True) else 0,
            )

        # Kick off background execution
        thread = threading.Thread(
            target=self._execute_run,
            args=(run_id, plan_name, source),
            daemon=True,
            name=f"hub-plan-run-{run_id[:20]}",
        )
        thread.start()

        logger.info("plan %s run %s started (source=%s)", plan_name, run_id, source)
        return StartPlanRunResult(run_id=run_id, status="running")

    def _execute_run(self, run_id: str, plan_name: str, source: str) -> None:
        """Execute a plan run in the background.

        Sequentially executes steps, updates step/run status, and computes
        next_run_at when done.
        """
        plan = self._store.get_scheduled_plan(plan_name)
        if not plan:
            self._store.update_scheduled_run(run_id, status="failed", error="plan not found during execution")
            return

        config = json.loads(plan["config_json"] or "{}")
        plan_timeout = config.get("wait_timeout_seconds", 3600)
        plan_poll_interval = config.get("poll_interval_seconds", 5)

        run_status = "succeeded"
        run_error = None
        failed = False

        step_rows = self._store.get_scheduled_run_steps(run_id)
        for step_row in step_rows:
            step_id = step_row["id"]
            command_name = step_row["command_name"]
            params = json.loads(step_row["params_json"] or "{}")
            wait_for_terminal = bool(step_row["wait_for_terminal"])

            # If a previous step failed, mark remaining as skipped
            if failed:
                self._store.update_scheduled_run_step(
                    step_id, status="skipped", error="previous step failed",
                )
                continue

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
                    job_id=exc.ingestion_job_id,
                )
                run_status = "failed"
                run_error = f"step {command_name} failed: {exc.message}"
                failed = True
                continue

            # Wait for terminal status if required
            if wait_for_terminal:
                # Step-level timeout overrides plan-level
                step_cfg = config.get("steps", [])
                step_idx = step_row["step_order"]
                step_timeout = plan_timeout
                if step_idx < len(step_cfg):
                    step_timeout = step_cfg[step_idx].get("wait_timeout_seconds", plan_timeout)

                step_status, is_timeout = self._wait_for_job_terminal(
                    job_result.ingestion_job_id,
                    timeout=step_timeout,
                    poll_interval=plan_poll_interval,
                )
                job_detail = self._store.get_job(job_result.ingestion_job_id)
                step_error = job_detail.get("error") if job_detail else None

                if is_timeout:
                    timeout_msg = f"wait timeout after {step_timeout}s"
                    self._store.update_scheduled_run_step(
                        step_id, status="failed", error=timeout_msg,
                        result_json=self._store._json(job_detail) if job_detail else None,
                    )
                    run_status = "failed"
                    run_error = f"step {command_name} {timeout_msg}"
                    failed = True
                else:
                    self._store.update_scheduled_run_step(
                        step_id, status=step_status, error=step_error,
                        result_json=self._store._json(job_detail) if job_detail else None,
                    )
                    if step_status == "failed":
                        run_status = "failed"
                        run_error = f"step {command_name} failed"
                        failed = True
                    elif step_status == "partial":
                        if run_status == "succeeded":
                            run_status = "partial"
            else:
                # Fire-and-forget: mark succeeded once submitted
                self._store.update_scheduled_run_step(step_id, status="succeeded")

        # Compute next_run_at: only for scheduler-triggered runs on daily plans
        next_run_at = None
        if source == "scheduler" and plan["schedule_type"] == "daily" and plan["schedule_time"]:
            next_run_at = self._compute_next_daily_run(plan)
        elif source != "scheduler" and plan["schedule_type"] == "daily" and plan["schedule_time"]:
            # Manual run: only fill next_run_at if it's currently empty
            current_plan = self._store.get_scheduled_plan(plan_name)
            if current_plan and not current_plan.get("next_run_at"):
                next_run_at = self._compute_next_daily_run(plan)

        # Finalize run
        self._store.update_scheduled_run(run_id, status=run_status, error=run_error)
        self._store.update_plan_last_run(plan_name, run_id=run_id, status=run_status, next_run_at=next_run_at)

        logger.info("plan %s run %s completed: %s (source=%s)", plan_name, run_id, run_status, source)

    def _compute_next_daily_run(self, plan: dict[str, Any]) -> str:
        """Compute the next daily run time for a plan.

        Uses: next_dt = today at schedule_time; if next_dt <= now, add 1 day.
        """
        tz = ZoneInfo(plan.get("timezone", "Asia/Shanghai"))
        now_tz = datahub_now().astimezone(tz)
        hour, minute = (int(x) for x in plan["schedule_time"].split(":"))
        next_dt = now_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_dt <= now_tz:
            next_dt += timedelta(days=1)
        return next_dt.strftime("%Y-%m-%d %H:%M:%S")

    # ── Scheduler tick ───────────────────────────────────────────

    def scheduler_tick(self) -> None:
        """Check enabled plans and trigger runs that are due.

        Called periodically by the collection scheduler background thread.
        Non-blocking: only calls run_plan_now which starts a background thread.
        Manual plans are skipped — they can only be triggered via run-now.
        """
        plans = self._store.list_scheduled_plans()
        now_text = datahub_now_text()

        for plan in plans:
            if not plan["enabled"]:
                continue
            # Manual plans are never auto-triggered by scheduler
            if plan["schedule_type"] == "manual":
                continue
            if not plan["next_run_at"]:
                continue
            if plan["next_run_at"] > now_text:
                continue

            # Check for overlapping run (mark_stale_runs called inside run_plan_now)
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

    # ── Helpers ──────────────────────────────────────────────────

    def _wait_for_job_terminal(self, ingestion_job_id: str, timeout: float = 3600, poll_interval: float = 5.0) -> tuple[str, bool]:
        """Poll until an ingestion_job reaches terminal status.

        Returns:
            (status, is_timeout): status is the job status string;
            is_timeout is True if the poll loop exhausted the timeout.
        """
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            job = self._store.get_job(ingestion_job_id)
            if job and job["status"] in _TERMINAL_STATUSES:
                return job["status"], False
            time.sleep(poll_interval)
        return "failed", True

    def mark_stale_runs(self, stale_seconds: int = 32400) -> int:
        """Mark running scheduled_runs as failed if they've been running too long.

        This handles crash recovery: if the process restarts with stale running runs,
        they get marked as failed so new runs can be triggered.

        Default stale_seconds is 32400 (9 hours) to accommodate long-running
        initial full load plans. Per-plan timeout is read from config_json
        wait_timeout_seconds; stale cutoff is max(stale_seconds, plan_timeout + 3600).
        """
        runs = self._store.list_scheduled_runs(limit=200)
        marked = 0
        for run in runs:
            if run["status"] != "running":
                continue
            # Determine per-plan stale cutoff
            plan_name = run.get("plan_name", "")
            plan = self._store.get_scheduled_plan(plan_name) if plan_name else None
            plan_stale = stale_seconds
            if plan:
                config = json.loads(plan.get("config_json") or "{}")
                plan_timeout = config.get("wait_timeout_seconds", 0)
                if plan_timeout:
                    plan_stale = max(stale_seconds, plan_timeout + 3600)

            cutoff = (datahub_now() - timedelta(seconds=plan_stale)).strftime("%Y-%m-%d %H:%M:%S")
            if run["started_at"] and run["started_at"] < cutoff:
                self._store.update_scheduled_run(run["run_id"], status="failed", error="stale run marked failed on restart")
                marked += 1
        if marked:
            logger.info("marked %d stale scheduled_runs as failed", marked)
        return marked
