from __future__ import annotations

import logging
import threading

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.datahub.api import (
    build_admin_router,
    build_health_router,
    build_ingestion_router,
    build_metadata_router,
    build_ops_router,
    build_schedules_router,
    register_query_routes,
)
from src.datahub.core.plugin_loader import build_normalizer_map, build_scope_map, load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.core.services.collection_plan_service import CollectionPlanService
from src.datahub.core.services.job_service import JobService
from src.datahub.core.trigger_runtime import ExternalSyncClient, poll_downloader_jobs
from src.datahub.core.fanout_scheduler import start_fanout_scheduler
from src.datahub.ingestion.service import IngestionService
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)


def _start_status_poller(store: DataHubStore, trigger_clients: dict[str, ExternalSyncClient], interval: float = 5.0, stale_threshold: int = 1800) -> threading.Event:
    """Start a background thread that polls downloader job status."""
    stop_event = threading.Event()

    def _poll_loop():
        while not stop_event.is_set():
            try:
                summary = poll_downloader_jobs(store, trigger_clients, stale_threshold_seconds=stale_threshold)
                if summary["updated"] > 0 or summary["stale"] > 0:
                    logger.info("status poll: %s", summary)
            except Exception:
                logger.exception("status poll error")
            stop_event.wait(timeout=interval)

    thread = threading.Thread(target=_poll_loop, daemon=True, name="hub-status-poller")
    thread.start()
    return stop_event


def _start_collection_scheduler(
    plan_service: CollectionPlanService,
    settings: Settings,
) -> threading.Event | None:
    """Start the collection scheduler background thread. Returns shutdown Event or None if disabled."""
    if not settings.collection_scheduler_enabled:
        logger.info("collection scheduler disabled (DATAHUB_COLLECTION_SCHEDULER_ENABLED not set)")
        return None

    # Seed default plans and enable daily_dcp_refresh if configured
    plan_service.seed_default_plans()
    if settings.daily_dcp_refresh_enabled:
        # Enable dcp_daily_update (the new business plan) instead of legacy daily_dcp_refresh
        plan = plan_service.get_plan("dcp_daily_update")
        if plan and not plan["enabled"]:
            import json
            from zoneinfo import ZoneInfo
            from src.datahub.core.time_utils import datahub_now
            from datetime import timedelta
            config = json.loads(plan["config_json"] or "{}")
            plan_service._store.upsert_scheduled_plan(
                plan_name="dcp_daily_update",
                enabled=1,
                schedule_type="daily",
                schedule_time=settings.daily_dcp_refresh_time,
                timezone="Asia/Shanghai",
                config_json=json.dumps(config, ensure_ascii=False),
            )
            tz = ZoneInfo("Asia/Shanghai")
            now_tz = datahub_now().astimezone(tz)
            hour, minute = (int(x) for x in settings.daily_dcp_refresh_time.split(":"))
            next_dt = now_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_dt <= now_tz:
                next_dt += timedelta(days=1)
            plan_service._store.update_plan_next_run("dcp_daily_update", next_dt.strftime("%Y-%m-%d %H:%M:%S"))
            logger.info("dcp_daily_update enabled, next run at %s", next_dt.strftime("%Y-%m-%d %H:%M:%S"))

    stop_event = threading.Event()
    tick_interval = float(settings.collection_scheduler_tick_seconds)

    def loop():
        while not stop_event.is_set():
            try:
                plan_service.scheduler_tick()
            except Exception as exc:
                logger.error("collection scheduler tick error: %s", exc, exc_info=True)
            stop_event.wait(tick_interval)

    thread = threading.Thread(target=loop, name="hub-collection-scheduler", daemon=True)
    thread.start()
    logger.info("collection scheduler started (tick=%ds)", settings.collection_scheduler_tick_seconds)
    return stop_event


def create_app(
    settings: Settings | None = None,
    store: DataHubStore | None = None,
    trigger_clients: dict[str, ExternalSyncClient] | None = None,
) -> FastAPI:
    active_settings = settings or Settings.from_env()
    plugins = load_all_plugins(active_settings.plugin_dir)
    registry = load_registry_from_plugins(plugins)
    active_store = store or DataHubStore(active_settings.db_path, registry, scope_mappings=build_scope_map(plugins))
    active_store.init_schema(dev_mode=active_settings.dev_mode)
    clients = trigger_clients or {plugin.name: ExternalSyncClient(plugin.connector) for plugin in plugins if plugin.connector.base_url}
    normalizer_map = build_normalizer_map(plugins)
    ingestion_service = IngestionService(active_store, normalizer_map=normalizer_map)
    callback_headers = {"X-API-Key": active_settings.callback_api_key} if active_settings.callback_api_key else None
    job_service = JobService(
        store=active_store,
        plugins=plugins,
        trigger_clients=clients,
        callback_base_url=active_settings.callback_base_url,
        callback_headers=callback_headers,
    )

    app = FastAPI(title="DataCollectorHub MVP", version="1.0.0")
    app.state.settings = active_settings
    app.state.plugins = plugins
    app.state.registry = registry
    app.state.store = active_store
    app.state.trigger_clients = clients
    app.state.job_service = job_service

    # Collection plan service
    plan_service = CollectionPlanService(
        store=active_store,
        job_service=job_service,
        recent_days=active_settings.daily_dcp_recent_days,
    )
    plan_service.seed_default_plans()
    # Always clean up stale runs on startup (regardless of scheduler enabled)
    plan_service.mark_stale_runs()
    app.state.plan_service = plan_service

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        logger.warning("RequestValidationError %s %s: %s", request.method, request.url.path, errors)
        return JSONResponse(status_code=422, content={"detail": errors})

    app.include_router(build_health_router(registry, store=active_store, settings=active_settings))
    app.include_router(build_metadata_router(plugins, registry))
    app.include_router(build_admin_router(active_store))
    app.include_router(build_ops_router(store=active_store, plugins=plugins))
    app.include_router(build_schedules_router(store=active_store, plan_service=plan_service))
    app.include_router(
        build_ingestion_router(
            settings=active_settings,
            plugins=plugins,
            store=active_store,
            trigger_clients=clients,
            ingestion_service=ingestion_service,
            job_service=job_service,
        )
    )
    register_query_routes(app, plugins, active_store)

    # Start background status poller for downloader_sync jobs
    if clients:
        app.state.status_poller_stop = _start_status_poller(active_store, clients, interval=5.0, stale_threshold=1800)
        logger.info("status poller started (interval=5s, stale_threshold=1800s)")

        # Start fan-out scheduler
        app.state.fanout_scheduler_stop = start_fanout_scheduler(
            active_store,
            clients,
            plugins,
            callback_base_url=active_settings.callback_base_url,
            callback_headers=callback_headers,
            tick_interval=3.0,
        )
        logger.info("fan-out scheduler started (tick=3s)")

    # Start collection scheduler (disabled by default)
    app.state.collection_scheduler_stop = _start_collection_scheduler(plan_service, active_settings)

    return app


app = create_app()
