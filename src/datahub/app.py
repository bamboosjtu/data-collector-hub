from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.datahub.api import (
    build_admin_router,
    build_health_router,
    build_ingestion_router,
    build_metadata_router,
    build_ops_router,
    register_query_routes,
)
from src.datahub.core.plugin_loader import build_normalizer_map, build_scope_map, load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.core.trigger_runtime import ExternalSyncClient
from src.datahub.ingestion.service import IngestionService
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)


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

    app = FastAPI(title="DataCollectorHub MVP", version="1.0.0")
    app.state.settings = active_settings
    app.state.plugins = plugins
    app.state.registry = registry
    app.state.store = active_store
    app.state.trigger_clients = clients

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        logger.warning("RequestValidationError %s %s: %s", request.method, request.url.path, errors)
        return JSONResponse(status_code=422, content={"detail": errors})

    app.include_router(build_health_router(registry))
    app.include_router(build_metadata_router(plugins, registry))
    app.include_router(build_admin_router(active_store))
    app.include_router(build_ops_router(store=active_store, plugins=plugins))
    app.include_router(
        build_ingestion_router(
            settings=active_settings,
            plugins=plugins,
            store=active_store,
            trigger_clients=clients,
            ingestion_service=ingestion_service,
        )
    )
    register_query_routes(app, plugins, active_store)
    return app


app = create_app()
