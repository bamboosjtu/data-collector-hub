from __future__ import annotations

import tempfile
import asyncio
import json
from pathlib import Path
from typing import Any

from src.datahub.app import create_app
from src.datahub.core.plugin_loader import build_scope_map, load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore


ROOT = Path(__file__).resolve().parents[1]


class FakeExternalClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def sync(self, *, producer_job_id: str, job_type: str, params: dict[str, Any], callback_url: str, debug: bool = False) -> dict[str, Any]:
        self.calls.append(
            {
                "producer_job_id": producer_job_id,
                "job_type": job_type,
                "params": params,
                "callback_url": callback_url,
                "debug": debug,
            }
        )
        return {"downloader_job_id": producer_job_id, "status": "accepted"}


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugins = load_all_plugins(ROOT / "plugins")
        registry = load_registry_from_plugins(plugins)
        store = DataHubStore(tmp_path / "datahub.sqlite", registry, build_scope_map(plugins))
        fake = FakeExternalClient()
        app = create_app(
            Settings(db_path=tmp_path / "datahub.sqlite", plugin_dir=ROOT / "plugins", callback_base_url="http://datahub.test"),
            store=store,
            trigger_clients={"dcp": fake},
        )
        assert request(app, "GET", "/health").json["status"] == "ok"
        assert request(app, "GET", "/metadata").status_code == 200
        assert request(app, "GET", "/plugins").status_code == 200
        assert request(app, "GET", "/schemas").status_code == 200

        payload = _progress_payload()
        assert request(app, "POST", "/ingestion/v1/table-batches", json_body=payload).status_code == 401
        assert request(app, "POST", "/ingestion/v1/table-batches", json_body=payload, headers=auth("dev-admin-key")).status_code == 200

        key_response = request(app, "POST", "/admin/api-keys", json_body={"name": "query", "scopes": ["query"]}, headers=auth("dev-admin-key"))
        query_key = key_response.json["token"]
        assert request(app, "POST", "/admin/api-keys", json_body={"name": "bad", "scopes": ["query"]}, headers=auth(query_key)).status_code == 401

        query = request(app, "GET", "/api/v1/plan/progress-management?planYear=2026", headers=auth(query_key))
        assert query.status_code == 200
        item = query.json["items"][0]
        assert item["prjCode"] == "P001"
        assert "_ingest_message_id" not in item

        job = request(app, "POST", "/ingestion/v1/jobs", json_body={"job_type": "project_tech_full", "params": {"projectCode": "P001"}}, headers=auth("dev-admin-key"))
        assert job.status_code == 202
        assert fake.calls[0]["job_type"] == "project_tech_full"
        assert fake.calls[0]["params"] == {"projectCode": "P001"}
        assert fake.calls[0]["callback_url"] == "http://datahub.test/ingestion/v1/table-batches"

        assert request(app, "POST", "/ingestion/v1/jobs", json_body={"job_type": "missing", "params": {}}, headers=auth("dev-admin-key")).status_code == 422
        assert request(app, "POST", "/ingestion/v1/jobs", json_body={"job_type": "project_tech_full", "params": {}}, headers=auth("dev-admin-key")).status_code == 422
    print("phase5 ok")


def auth(token: str) -> dict[str, str]:
    return {"X-API-Key": token}


class Response:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self.body = body
        self.json = json.loads(body.decode("utf-8")) if body else None


def request(app, method: str, target: str, *, json_body: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Response:
    return asyncio.run(_request(app, method, target, json_body=json_body, headers=headers or {}))


async def _request(app, method: str, target: str, *, json_body: dict[str, Any] | None, headers: dict[str, str]) -> Response:
    path, _, query = target.partition("?")
    body = b"" if json_body is None else json.dumps(json_body).encode("utf-8")
    response_status = 500
    response_body = bytearray()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": query.encode("ascii"),
        "headers": [(key.lower().encode("ascii"), value.encode("utf-8")) for key, value in headers.items()] + [(b"content-type", b"application/json")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    received = False

    async def receive():
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        nonlocal response_status
        if message["type"] == "http.response.start":
            response_status = message["status"]
        elif message["type"] == "http.response.body":
            response_body.extend(message.get("body", b""))

    await app(scope, receive, send)
    return Response(response_status, bytes(response_body))


def _progress_payload() -> dict:
    return {
        "message_id": "msg_api_1",
        "idempotency_key": "idem_api_1",
        "downloader_job_id": "job_api",
        "collect_run_id": "collect_api",
        "dataset_key": "plan_professional",
        "scope_key": "planYear:2026",
        "payload_hash": "sha256:api",
        "tables": [
            {
                "table_name": "dcp_plan_progress_management",
                "scope_values": {"planYear": "2026"},
                "rows": [{"planYear": "2026", "id": "api_1", "prjCode": "P001"}],
            }
        ],
    }


if __name__ == "__main__":
    main()
