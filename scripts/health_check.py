from __future__ import annotations

import argparse
import json
import sys

from core.paths import DEFAULT_DB_PATH
from health.summary import get_health_summary
from storage.sqlite_store import SQLiteStore


def _exit_code(status: str) -> int:
    if status == "failed":
        return 2
    if status == "warning":
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="DataHub health check")
    parser.add_argument("--recent-days", type=int, default=14)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    store = SQLiteStore(DEFAULT_DB_PATH)
    summary = get_health_summary(store, recent_days=args.recent_days)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        return _exit_code(summary["overall_status"])

    print(f"overall_status: {summary['overall_status']}")
    if summary["reasons"]:
        print("reasons:")
        for reason in summary["reasons"]:
            print(f"  - {reason}")

    print("dataset_counts:")
    for dataset_key, item in summary["dataset_health"]["datasets"].items():
        print(
            f"  - {dataset_key}: raw_events={item['raw_event_count']} "
            f"canonical={item['canonical_entity_count']} relationships={item['relationship_count']}"
        )

    print("domain_counts:")
    print(
        f"  entities={summary['domain_health']['entity_counts']} "
        f"relationships={summary['domain_health']['relationship_counts']}"
    )

    print("job_counts:")
    print(f"  external={summary['job_health']['external_collection_jobs']['counts']}")
    print(f"  processing={summary['job_health']['processing_jobs']['counts']}")

    return _exit_code(summary["overall_status"])


if __name__ == "__main__":
    sys.exit(main())

