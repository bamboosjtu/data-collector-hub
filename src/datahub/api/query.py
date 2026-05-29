from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, Request

from src.datahub.core.specs import PluginSpec, QueryRouteSpec
from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope


def register_query_routes(app: FastAPI, plugins: list[PluginSpec], store: DataHubStore) -> None:
    for plugin in plugins:
        for route_spec in plugin.query_routes:
            _register_query_route(app, route_spec, store)


def _register_query_route(app: FastAPI, route: QueryRouteSpec, store: DataHubStore) -> None:
    def handler(request: Request, _route: QueryRouteSpec = route) -> dict[str, Any]:
        filters: dict[str, Any] = {}
        path_params = dict(request.path_params)
        for col, param_name in _route.path_filters.items():
            if param_name in path_params:
                filters[col] = path_params[param_name]
        query_params = dict(request.query_params)
        for col, param_name in _route.query_filters.items():
            if param_name in query_params:
                filters[col] = query_params[param_name]
        limit = min(int(query_params.get("limit", _route.default_limit)), _route.max_limit)
        return {"items": store.query_table(_route.table, filters, limit=limit)}

    app.add_api_route(
        route.path,
        handler,
        methods=["GET"],
        dependencies=[Depends(require_scope(store, "query"))],
        name=f"query_{route.table}",
        summary=f"Query {route.table}",
    )
