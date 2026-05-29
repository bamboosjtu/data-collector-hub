from .admin import build_admin_router
from .health import build_health_router
from .ingestion import build_ingestion_router
from .metadata import build_metadata_router
from .query import register_query_routes

__all__ = [
    "build_admin_router",
    "build_health_router",
    "build_ingestion_router",
    "build_metadata_router",
    "register_query_routes",
]
