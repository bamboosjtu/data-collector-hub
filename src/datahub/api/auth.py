from __future__ import annotations

import logging

from fastapi import Header, HTTPException, status

from src.datahub.storage.sqlite import DataHubStore

logger = logging.getLogger(__name__)


def require_scope(store: DataHubStore, scope: str):
    def dependency(x_api_key: str | None = Header(default=None)) -> None:
        # TODO: Auth enforcement is deferred until downstream producers support
        # per-job callback headers. Currently, downloader-dcp's OutboxDispatcher
        # only uses global headers and ignores per-job sink.headers, causing 401
        # on callbacks. When downloader-dcp supports per-job headers, re-enable
        # strict auth by removing the bypass below.
        if x_api_key is not None:
            if not store.verify_api_key(x_api_key, scope):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid API key for scope: {scope}")
            return
        # No API key provided — log warning but allow in current version
        logger.warning("request without X-API-Key to scope=%s (auth deferred)", scope)

    return dependency
