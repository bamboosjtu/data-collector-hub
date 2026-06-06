from __future__ import annotations

import json
from typing import Any
from urllib import request
from uuid import uuid4

from .specs import CommandSpec, ConnectorSpec


class ExternalSyncClient:
    def __init__(self, connector: ConnectorSpec):
        self.connector = connector
        self.base_url = connector.base_url.rstrip("/")
        self.timeout_seconds = connector.timeout_seconds

    def sync(self, *, producer_job_id: str, job_type: str, params: dict[str, Any], callback_url: str, debug: bool = False) -> dict[str, Any]:
        return self._json(
            "/sync",
            "POST",
            {
                "downloader_job_id": producer_job_id,
                "job_type": job_type,
                "params": params,
                "sink": {"type": "http_callback", "url": callback_url},
                "debug": debug,
            },
        )

    def _json(self, path: str, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(f"{self.base_url}{path}", data=data, method=method, headers={"Content-Type": "application/json"})
        opener = request.build_opener(request.ProxyHandler({}))
        with opener.open(req, timeout=self.timeout_seconds) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}


def new_producer_job_id(command_name: str, params: dict[str, Any], command: CommandSpec | None = None) -> str:
    suffix = None
    if command:
        for param in command.required_params:
            if params.get(param):
                suffix = str(params[param])
                break
    if not suffix:
        suffix = uuid4().hex[:12]
    safe_suffix = suffix.replace(":", "_").replace("/", "_").replace("\\", "_")
    return f"job_{command_name}_{safe_suffix}_{uuid4().hex[:8]}"
