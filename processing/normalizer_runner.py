from __future__ import annotations

from typing import Any

from plugins.dcp_response_registry import DCP_RESPONSE_TABLES
from processing.response_canonical import RESPONSE_CANONICAL_VERSION, project_raw_event
from storage.sqlite_store import SQLiteStore


MONITOR_PROCESSING_DATASETS = ["daily_meeting", "tower", "station"]


def supported_datasets(include_domain: bool = False) -> list[str]:
    datasets = sorted({entry["dataset_key"] for entry in DCP_RESPONSE_TABLES})
    if include_domain:
        return datasets
    return [dataset for dataset in MONITOR_PROCESSING_DATASETS if dataset in datasets]


class NormalizerRunner:
    """Project raw_events into response-aligned canonical current tables."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def _update_raw_event_processing_status(
        self,
        raw_event_id: int,
        *,
        status: str,
        error: str | None,
    ) -> None:
        updater = getattr(self.store, "update_raw_event_processing_status", None)
        if callable(updater):
            updater(raw_event_id, status=status, error=error)

    def run(
        self,
        dataset_key: str,
        batch_size: int = 1000,
        mode: str = "incremental",
    ) -> dict[str, Any]:
        if dataset_key not in supported_datasets(include_domain=True):
            return {
                "processed": 0,
                "inserted": 0,
                "updated": 0,
                "ignored_older": 0,
                "relationships_inserted": 0,
                "relationships_updated": 0,
                "skipped": 0,
                "failed": 1,
                "last_raw_event_id": None,
                "errors": [f"unsupported dataset_key: {dataset_key}"],
            }
        if mode not in {"incremental", "full"}:
            return {
                "processed": 0,
                "inserted": 0,
                "updated": 0,
                "ignored_older": 0,
                "relationships_inserted": 0,
                "relationships_updated": 0,
                "skipped": 0,
                "failed": 1,
                "last_raw_event_id": None,
                "errors": [f"unsupported processing mode: {mode}"],
            }

        state = self.store.get_normalizer_state(dataset_key)
        state_version = state.get("normalizer_version")
        last_raw_event_id = (
            int(state.get("last_raw_event_id") or 0)
            if mode == "incremental" and state_version == RESPONSE_CANONICAL_VERSION
            else 0
        )
        offset = 0
        processed = inserted = updated = ignored_older = 0
        relationships_inserted = relationships_updated = 0
        skipped = failed = 0
        errors: list[str] = []

        while True:
            raw_events = self.store.list_raw_events(
                dataset_key=dataset_key,
                limit=batch_size,
                after_id=last_raw_event_id if mode == "incremental" else None,
                offset=offset if mode == "full" else 0,
            )
            if not raw_events:
                break
            batch_last_raw_event_id = last_raw_event_id
            failed_in_batch = False
            for raw_event in raw_events:
                raw_event_id = int(raw_event.get("id") or 0)
                rows, relationships, error = project_raw_event(raw_event)
                if error and not rows:
                    skipped += 1
                    errors.append(f"raw_event_id={raw_event_id}: {error}")
                    self._update_raw_event_processing_status(raw_event_id, status="skipped", error=error)
                    batch_last_raw_event_id = max(batch_last_raw_event_id, raw_event_id)
                    continue
                try:
                    for row in rows:
                        status = self.store.upsert_response_canonical_row(row)
                        processed += 1
                        if status == "inserted":
                            inserted += 1
                        elif status == "updated":
                            updated += 1
                        elif status == "ignored_older":
                            ignored_older += 1
                    for relationship in relationships:
                        rel_status = self.store.upsert_canonical_relationship(**relationship)
                        if rel_status == "inserted":
                            relationships_inserted += 1
                        elif rel_status == "updated":
                            relationships_updated += 1
                    self._update_raw_event_processing_status(raw_event_id, status="processed", error=None)
                    batch_last_raw_event_id = max(batch_last_raw_event_id, raw_event_id)
                except Exception as exc:
                    failed += 1
                    failed_in_batch = True
                    errors.append(f"raw_event_id={raw_event_id}: {exc}")
                    self._update_raw_event_processing_status(raw_event_id, status="failed", error=str(exc))
                    break
            if failed_in_batch:
                break
            if batch_last_raw_event_id > last_raw_event_id:
                self.store.save_normalizer_state(dataset_key, batch_last_raw_event_id, RESPONSE_CANONICAL_VERSION)
                last_raw_event_id = batch_last_raw_event_id
            if len(raw_events) < batch_size:
                break
            if mode == "full":
                offset += batch_size

        if failed == 0:
            self.store.save_normalizer_state(dataset_key, last_raw_event_id, RESPONSE_CANONICAL_VERSION)
        return {
            "processed": processed,
            "inserted": inserted,
            "updated": updated,
            "ignored_older": ignored_older,
            "relationships_inserted": relationships_inserted,
            "relationships_updated": relationships_updated,
            "skipped": skipped,
            "failed": failed,
            "last_raw_event_id": last_raw_event_id,
            "errors": errors,
        }
