"""Tests for DataHub timezone-aware time utilities."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from src.datahub.core.time_utils import (
    DATAHUB_TZ,
    datahub_current_year,
    datahub_days_ago,
    datahub_now,
    datahub_now_text,
    datahub_today,
    datahub_yesterday,
)


class TestDatahubNow:
    def test_returns_beijing_time(self):
        result = datahub_now()
        assert result.tzinfo == DATAHUB_TZ

    def test_beijing_hour_offset(self):
        """Beijing time should be UTC+8."""
        result = datahub_now()
        utc_now = datetime.now(ZoneInfo("UTC"))
        # Same instant, so difference should be near zero
        # But Beijing hour should be 8 ahead of UTC hour
        beijing_hour = result.hour
        utc_hour = utc_now.hour
        expected_diff = (beijing_hour - utc_hour) % 24
        assert expected_diff == 8 or (result.date() != utc_now.date() and expected_diff in (8, 16))


class TestDatahubToday:
    def test_utc_16_30_is_next_day_beijing(self):
        """UTC 2026-06-07 16:30 = Beijing 2026-06-08 00:30 → today = 2026-06-08."""
        fake_utc = datetime(2026, 6, 7, 16, 30, 0, tzinfo=ZoneInfo("UTC"))
        with patch("src.datahub.core.time_utils.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc.astimezone(DATAHUB_TZ)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            assert datahub_today() == date(2026, 6, 8)

    def test_utc_08_00_same_day_beijing(self):
        """UTC 2026-06-07 08:00 = Beijing 2026-06-07 16:00 → today = 2026-06-07."""
        fake_utc = datetime(2026, 6, 7, 8, 0, 0, tzinfo=ZoneInfo("UTC"))
        with patch("src.datahub.core.time_utils.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc.astimezone(DATAHUB_TZ)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            assert datahub_today() == date(2026, 6, 7)


class TestDatahubYesterday:
    def test_yesterday_is_today_minus_one(self):
        fake_utc = datetime(2026, 6, 7, 16, 30, 0, tzinfo=ZoneInfo("UTC"))
        with patch("src.datahub.core.time_utils.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc.astimezone(DATAHUB_TZ)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            assert datahub_yesterday() == date(2026, 6, 7)


class TestDatahubDaysAgo:
    def test_7_days_ago(self):
        fake_utc = datetime(2026, 6, 7, 16, 30, 0, tzinfo=ZoneInfo("UTC"))
        with patch("src.datahub.core.time_utils.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc.astimezone(DATAHUB_TZ)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            assert datahub_days_ago(7) == date(2026, 6, 1)


class TestDatahubCurrentYear:
    def test_year_cross_beijing(self):
        """UTC 2026-12-31 16:30 = Beijing 2027-01-01 00:30 → year = '2027'."""
        fake_utc = datetime(2026, 12, 31, 16, 30, 0, tzinfo=ZoneInfo("UTC"))
        with patch("src.datahub.core.time_utils.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc.astimezone(DATAHUB_TZ)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            assert datahub_current_year() == "2027"

    def test_normal_year(self):
        """UTC 2026-06-07 08:00 = Beijing 2026-06-07 16:00 → year = '2026'."""
        fake_utc = datetime(2026, 6, 7, 8, 0, 0, tzinfo=ZoneInfo("UTC"))
        with patch("src.datahub.core.time_utils.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc.astimezone(DATAHUB_TZ)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            assert datahub_current_year() == "2026"


class TestDatahubNowText:
    def test_format(self):
        result = datahub_now_text()
        # Should be "YYYY-MM-DD HH:MM:SS"
        assert len(result) == 19
        assert result[4] == "-"
        assert result[7] == "-"
        assert result[10] == " "
        assert result[13] == ":"
        assert result[16] == ":"

    def test_parsable(self):
        result = datahub_now_text()
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None
