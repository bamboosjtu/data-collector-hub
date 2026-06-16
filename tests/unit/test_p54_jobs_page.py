"""Tests for P5.4: Server-side pagination and filtering for Jobs."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.datahub.core.plugin_loader import load_all_plugins
from src.datahub.core.registry import load_registry_from_plugins
from src.datahub.settings import Settings
from src.datahub.storage.sqlite import DataHubStore


@pytest.fixture
def store():
    d = tempfile.mkdtemp()
    db_path = str(Path(d) / "test_p54.db")
    plugins = load_all_plugins(Settings.plugin_dir)
    registry = load_registry_from_plugins(plugins)
    s = DataHubStore(db_path, registry)
    s.init_schema(dev_mode=True)
    return s


def _insert_job(store, job_id, *, status="succeeded", source="api",
                trigger_key="test_cmd", parent_job_id=None,
                retry_of_job_id=None, error=None):
    with store.connect() as conn:
        conn.execute(
            "INSERT INTO ingestion_jobs "
            "(ingestion_job_id, trigger_key, status, source, parent_job_id, retry_of_job_id, error, params_json, plugin_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, '{}', 'dcp')",
            (job_id, trigger_key, status, source, parent_job_id, retry_of_job_id, error),
        )


class TestListJobsPageBasic:

    def test_limit_offset_correct(self, store):
        """limit/offset returns correct page."""
        for i in range(15):
            _insert_job(store, f"job_{i:03d}")

        page1 = store.list_jobs_page(limit=5, offset=0)
        assert len(page1["items"]) == 5
        assert page1["total"] == 15
        assert page1["limit"] == 5
        assert page1["offset"] == 0

        page2 = store.list_jobs_page(limit=5, offset=5)
        assert len(page2["items"]) == 5
        assert page2["total"] == 15
        assert page2["offset"] == 5

        page3 = store.list_jobs_page(limit=5, offset=10)
        assert len(page3["items"]) == 5

        page4 = store.list_jobs_page(limit=5, offset=15)
        assert len(page4["items"]) == 0
        assert page4["total"] == 15

    def test_total_unaffected_by_limit(self, store):
        """total reflects all matching rows, not just the page."""
        for i in range(10):
            _insert_job(store, f"job_{i:03d}")

        result = store.list_jobs_page(limit=3, offset=0)
        assert result["total"] == 10
        assert len(result["items"]) == 3

    def test_max_limit_1000(self, store):
        """limit > 1000 is capped to 1000."""
        result = store.list_jobs_page(limit=5000)
        assert result["limit"] == 1000


class TestListJobsPageFilters:

    def test_status_filter(self, store):
        """status filter returns only matching jobs."""
        _insert_job(store, "job_s1", status="succeeded")
        _insert_job(store, "job_f1", status="failed")
        _insert_job(store, "job_r1", status="running")

        result = store.list_jobs_page(status="failed")
        assert result["total"] == 1
        assert result["items"][0]["ingestion_job_id"] == "job_f1"

    def test_source_filter(self, store):
        """source filter returns only matching jobs."""
        _insert_job(store, "job_api", source="api")
        _insert_job(store, "job_sched", source="scheduler")

        result = store.list_jobs_page(source="scheduler")
        assert result["total"] == 1
        assert result["items"][0]["ingestion_job_id"] == "job_sched"

    def test_parent_job_id_filter(self, store):
        """parent_job_id filter returns only child jobs."""
        _insert_job(store, "parent_1", trigger_key="parent_cmd")
        _insert_job(store, "child_1", parent_job_id="parent_1")
        _insert_job(store, "child_2", parent_job_id="parent_1")
        _insert_job(store, "orphan_1")

        result = store.list_jobs_page(parent_job_id="parent_1")
        assert result["total"] == 2

    def test_retry_of_job_id_filter(self, store):
        """retry_of_job_id filter returns only retry jobs."""
        _insert_job(store, "orig_1", status="failed")
        _insert_job(store, "retry_1", retry_of_job_id="orig_1")
        _insert_job(store, "other_1")

        result = store.list_jobs_page(retry_of_job_id="orig_1")
        assert result["total"] == 1
        assert result["items"][0]["ingestion_job_id"] == "retry_1"

    def test_trigger_key_filter(self, store):
        """trigger_key filter returns only matching jobs."""
        _insert_job(store, "job_a", trigger_key="refresh_towers")
        _insert_job(store, "job_b", trigger_key="backfill_meetings")

        result = store.list_jobs_page(trigger_key="refresh_towers")
        assert result["total"] == 1

    def test_combined_filters(self, store):
        """Multiple filters combine with AND."""
        _insert_job(store, "j1", status="failed", source="api")
        _insert_job(store, "j2", status="failed", source="scheduler")
        _insert_job(store, "j3", status="succeeded", source="api")

        result = store.list_jobs_page(status="failed", source="api")
        assert result["total"] == 1
        assert result["items"][0]["ingestion_job_id"] == "j1"


class TestListJobsPageSearch:

    def test_q_search_job_id(self, store):
        """q search matches ingestion_job_id."""
        _insert_job(store, "ing_special_prefix_123")
        _insert_job(store, "ing_other_456")

        result = store.list_jobs_page(q="special_prefix")
        assert result["total"] == 1

    def test_q_search_trigger_key(self, store):
        """q search matches trigger_key."""
        _insert_job(store, "job_1", trigger_key="refresh_towers_for_project")
        _insert_job(store, "job_2", trigger_key="backfill_meetings")

        result = store.list_jobs_page(q="towers")
        assert result["total"] == 1

    def test_q_search_error(self, store):
        """q search matches error field."""
        _insert_job(store, "job_1", error="dcp_remote_failure: timeout")
        _insert_job(store, "job_2", error="schema_mismatch")

        result = store.list_jobs_page(q="timeout")
        assert result["total"] == 1

    def test_q_search_parent_job_id(self, store):
        """q search matches parent_job_id."""
        _insert_job(store, "parent_xyz")
        _insert_job(store, "child_1", parent_job_id="parent_xyz")
        _insert_job(store, "child_2")

        result = store.list_jobs_page(q="parent_xyz")
        # Should match child_1 (parent_job_id) and parent_xyz (ingestion_job_id)
        assert result["total"] == 2

    def test_q_search_no_match(self, store):
        """q search with no match returns empty."""
        _insert_job(store, "job_1")
        result = store.list_jobs_page(q="nonexistent_xyz")
        assert result["total"] == 0


class TestListJobsPageOrder:

    def test_ordered_by_id_desc(self, store):
        """Results are ordered by id DESC (newest first)."""
        for i in range(5):
            _insert_job(store, f"job_{i:03d}")

        result = store.list_jobs_page(limit=3)
        ids = [item["ingestion_job_id"] for item in result["items"]]
        assert ids == ["job_004", "job_003", "job_002"]


class TestBackwardCompatibility:

    def test_old_list_jobs_still_works(self, store):
        """Old list_jobs method still returns list."""
        _insert_job(store, "job_1")
        _insert_job(store, "job_2")

        result = store.list_jobs(limit=10)
        assert isinstance(result, list)
        assert len(result) == 2


# ── P5.4.1: get_jobs_summary tests ──

class TestGetJobsSummary:

    def test_all_filter_summary_counts_all_failed(self, store):
        """Summary counts all failed jobs regardless of limit/offset."""
        for i in range(5):
            _insert_job(store, f"job_s_{i}", status="succeeded")
        for i in range(3):
            _insert_job(store, f"job_f_{i}", status="failed")
        for i in range(2):
            _insert_job(store, f"job_r_{i}", status="running")

        summary = store.get_jobs_summary()
        assert summary["total"] == 10
        assert summary["failed"] == 3
        assert summary["succeeded"] == 5
        assert summary["running"] == 2

    def test_status_failed_total_equals_failed(self, store):
        """When status=failed, total should equal failed count."""
        _insert_job(store, "job_s1", status="succeeded")
        _insert_job(store, "job_f1", status="failed")
        _insert_job(store, "job_f2", status="failed")

        summary = store.get_jobs_summary(status="failed")
        assert summary["total"] == 2
        assert summary["failed"] == 2

    def test_source_filter(self, store):
        """Source filter applies to summary."""
        _insert_job(store, "job_api", source="api", status="succeeded")
        _insert_job(store, "job_sched", source="scheduler", status="failed")
        _insert_job(store, "job_retry", source="retry", status="succeeded")

        summary = store.get_jobs_summary(source="scheduler")
        assert summary["total"] == 1
        assert summary["failed"] == 1

    def test_parent_job_id_filter(self, store):
        """parent_job_id filter applies to summary."""
        _insert_job(store, "parent_1")
        _insert_job(store, "child_1", parent_job_id="parent_1", status="succeeded")
        _insert_job(store, "child_2", parent_job_id="parent_1", status="failed")
        _insert_job(store, "orphan_1", status="succeeded")

        summary = store.get_jobs_summary(parent_job_id="parent_1")
        assert summary["total"] == 2
        assert summary["failed"] == 1

    def test_q_filter(self, store):
        """q search applies to summary."""
        _insert_job(store, "job_tower_1", trigger_key="refresh_towers", status="failed")
        _insert_job(store, "job_meeting_1", trigger_key="backfill_meetings", status="succeeded")

        summary = store.get_jobs_summary(q="towers")
        assert summary["total"] == 1
        assert summary["failed"] == 1

    def test_retry_count(self, store):
        """retry counts jobs with source='retry'."""
        _insert_job(store, "job_normal", source="api", status="succeeded")
        _insert_job(store, "job_retry_1", source="retry", status="succeeded")
        _insert_job(store, "job_retry_2", source="retry", status="failed")

        summary = store.get_jobs_summary()
        assert summary["retry"] == 2

    def test_running_includes_triggering_accepted(self, store):
        """running counts running/triggering/accepted/submitted."""
        _insert_job(store, "job_r1", status="running")
        _insert_job(store, "job_t1", status="triggering")
        _insert_job(store, "job_a1", status="accepted")
        _insert_job(store, "job_sub1", status="submitted")

        summary = store.get_jobs_summary()
        assert summary["running"] == 4

    def test_empty_db(self, store):
        """Empty DB returns zeros."""
        summary = store.get_jobs_summary()
        assert summary["total"] == 0
        assert summary["failed"] == 0
        assert summary["running"] == 0

    def test_list_jobs_page_no_regression(self, store):
        """list_jobs_page still works after refactoring to _build_jobs_where."""
        _insert_job(store, "job_1", status="succeeded")
        _insert_job(store, "job_2", status="failed")

        result = store.list_jobs_page(status="failed")
        assert result["total"] == 1
        assert len(result["items"]) == 1
