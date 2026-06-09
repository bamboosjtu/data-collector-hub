from __future__ import annotations

import tempfile
from pathlib import Path

from src.datahub.core.plugin_loader import build_scope_map, load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.ingestion.service import IngestionService
from src.datahub.storage.sqlite import DataHubStore


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugins = load_all_plugins(ROOT / "plugins")
        registry = load_registry_from_plugins(plugins)
        store = DataHubStore(Path(tmp) / "datahub.sqlite", registry, build_scope_map(plugins))
        store.init_schema()
        service = IngestionService(store)

        payload = _progress_payload("msg_ingest_1", "idem_ingest_1", "sha256:1")
        assert service.ingest_table_batch(payload)["status"] == "accepted"
        assert service.ingest_table_batch(payload)["status"] == "duplicate_accepted"
        conflict = dict(payload)
        conflict["payload_hash"] = "sha256:changed"
        assert service.ingest_table_batch(conflict)["error_code"] == "payload_hash_conflict"

        idem_conflict = _progress_payload("msg_ingest_2", "idem_ingest_1", "sha256:2")
        assert service.ingest_table_batch(idem_conflict)["error_code"] == "idempotency_conflict"

        bad_dataset = _progress_payload("msg_bad_dataset", "idem_bad_dataset", "sha256:bd")
        bad_dataset["dataset_key"] = "missing"
        assert service.ingest_table_batch(bad_dataset)["error_code"] == "unknown_dataset"

        bad_table = _progress_payload("msg_bad_table", "idem_bad_table", "sha256:bt")
        bad_table["tables"][0]["table_name"] = "missing_table"
        assert service.ingest_table_batch(bad_table)["error_code"] == "unknown_table"

        mismatch = _progress_payload("msg_mismatch", "idem_mismatch", "sha256:mm")
        mismatch["dataset_key"] = "safety_daily_meeting"
        assert service.ingest_table_batch(mismatch)["error_code"] == "table_dataset_mismatch"

        unknown_col = _progress_payload("msg_unknown_col", "idem_unknown_col", "sha256:uc")
        unknown_col["tables"][0]["rows"][0]["rawDcpField"] = "blocked"
        assert service.ingest_table_batch(unknown_col)["error_code"] == "schema_mismatch"

        missing_pk = _progress_payload("msg_missing_pk", "idem_missing_pk", "sha256:pk")
        del missing_pk["tables"][0]["rows"][0]["id"]
        assert service.ingest_table_batch(missing_pk)["error_code"] == "schema_mismatch"

        replace_missing_scope = {
            "message_id": "msg_scope",
            "idempotency_key": "idem_scope",
            "downloader_job_id": "job_scope",
            "collect_run_id": "collect_scope",
            "dataset_key": "year_progress_project_domain",
            "scope_key": None,
            "payload_hash": "sha256:scope",
            "tables": [{"table_name": "dcp_year_progress_project_domain", "scope_values": {}, "rows": [{"year": "2026", "id": "x"}]}],
        }
        assert service.ingest_table_batch(replace_missing_scope)["error_code"] == "missing_scope_values"
    print("phase4 ok")


def _progress_payload(message_id: str, idempotency_key: str, payload_hash: str) -> dict:
    return {
        "message_id": message_id,
        "idempotency_key": idempotency_key,
        "downloader_job_id": f"job_{message_id}",
        "collect_run_id": f"collect_{message_id}",
        "dataset_key": "plan_professional",
        "scope_key": "planYear:2026",
        "payload_hash": payload_hash,
        "tables": [
            {
                "table_name": "dcp_plan_progress_management",
                "scope_values": {"planYear": "2026"},
                "rows": [{"planYear": "2026", "id": f"row_{message_id}", "prjCode": "P001"}],
            }
        ],
    }


if __name__ == "__main__":
    main()
