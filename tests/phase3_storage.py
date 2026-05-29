from __future__ import annotations

import tempfile
from contextlib import closing
from pathlib import Path

from src.datahub.core.plugin_loader import build_scope_map, load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.core.specs import ColumnSpec, TableSpec
from src.datahub.storage.ddl import create_business_table, create_metadata_tables
from src.datahub.storage.sqlite import DataHubStore
from src.datahub.storage.writer import write_table


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugins = load_all_plugins(ROOT / "plugins")
        registry = load_registry_from_plugins(plugins)
        store = DataHubStore(tmp_path / "datahub.sqlite", registry, scope_mappings=build_scope_map(plugins))
        store.init_schema()
        with closing(store.connect()) as conn:
            existing = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert set(registry.tables).issubset(existing)

        payload = _payload("msg_store_1", "hash1")
        table = registry.tables["dcp_plan_progress_management"]
        with closing(store.connect()) as conn, conn:
            write_table(conn, table, [{"planYear": "2026", "id": "row1", "prjCode": "P1"}], {"planYear": "2026"}, payload, None)
            write_table(conn, table, [{"planYear": "2026", "id": "row1", "prjCode": "P2"}], {"planYear": "2026"}, _payload("msg_store_2", "hash2"), None)
            row = conn.execute("SELECT prjCode FROM dcp_plan_progress_management WHERE id = 'row1'").fetchone()
            assert row["prjCode"] == "P2"

        replace_table = registry.tables["dcp_year_progress_project_domain"]
        with closing(store.connect()) as conn, conn:
            write_table(conn, replace_table, [{"year": "2026", "id": "a", "prjCode": "A"}], {"year": "2026"}, _payload("msg_rep_1", "h1"), None)
            write_table(conn, replace_table, [{"year": "2026", "id": "b", "prjCode": "B"}], {"year": "2026"}, _payload("msg_rep_2", "h2"), None)
            rows = conn.execute("SELECT id FROM dcp_year_progress_project_domain WHERE year = '2026'").fetchall()
            assert [row["id"] for row in rows] == ["b"]

        append_table = TableSpec(
            table_name="append_events",
            dataset_key="append",
            description="append test",
            write_mode="append",
            primary_key=(),
            scope_column_names=(),
            columns={"id": ColumnSpec("id", "string", False)},
        )
        with closing(store.connect()) as conn, conn:
            create_metadata_tables(conn)
            create_business_table(conn, append_table)
            payload_append = _payload("msg_append", "ha")
            write_table(conn, append_table, [{"id": "1"}, {"id": "2"}], {}, payload_append, None)
            write_table(conn, append_table, [{"id": "1"}, {"id": "2"}], {}, payload_append, None)
            count = conn.execute("SELECT COUNT(*) AS c FROM append_events").fetchone()["c"]
            assert count == 2
    print("phase3 ok")


def _payload(message_id: str, payload_hash: str) -> dict:
    return {
        "message_id": message_id,
        "downloader_job_id": "job",
        "collect_run_id": "collect",
        "payload_hash": payload_hash,
    }


if __name__ == "__main__":
    main()
