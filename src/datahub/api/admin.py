from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends

from src.datahub.storage.sqlite import DataHubStore

from .auth import require_scope


class ApiKeyRequest(BaseModel):
    name: str
    scopes: list[str]


def build_admin_router(store: DataHubStore) -> APIRouter:
    router = APIRouter()

    @router.post("/admin/api-keys", dependencies=[Depends(require_scope(store, "admin"))])
    def create_key(payload: ApiKeyRequest) -> dict:
        return store.create_api_key(payload.name, payload.scopes)

    return router
