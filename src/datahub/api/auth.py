from __future__ import annotations

from fastapi import Header, HTTPException, status

from src.datahub.storage.sqlite import DataHubStore


def require_scope(store: DataHubStore, scope: str):
    def dependency(x_api_key: str | None = Header(default=None)) -> None:
        if not store.verify_api_key(x_api_key, scope):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"missing API key scope: {scope}")

    return dependency
