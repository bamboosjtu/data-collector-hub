"""Tests for CLI argument parsing, especially --params handling."""
import argparse
import pytest

from src.datahub.cli import main, cmd_trigger


class TestCliParamsParsing:
    """Test that --params supports both space-separated and repeated flag styles."""

    def _make_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--params", nargs="+", action="append")
        return parser

    def _parse_params(self, argv: list[str]) -> dict[str, str]:
        """Simulate cmd_trigger params parsing logic."""
        parser = self._make_parser()
        args = parser.parse_args(argv)
        params = {}
        for group in (args.params or []):
            for p in group:
                k, _, v = p.partition("=")
                params[k] = v
        return params

    def test_space_separated_single_flag(self):
        """--params max_items=5 max_concurrency=1 cooldown_seconds=5"""
        result = self._parse_params(["--params", "max_items=5", "max_concurrency=1", "cooldown_seconds=5"])
        assert result == {"max_items": "5", "max_concurrency": "1", "cooldown_seconds": "5"}

    def test_repeated_flags(self):
        """--params max_items=5 --params max_concurrency=1 --params cooldown_seconds=5"""
        result = self._parse_params(["--params", "max_items=5", "--params", "max_concurrency=1", "--params", "cooldown_seconds=5"])
        assert result == {"max_items": "5", "max_concurrency": "1", "cooldown_seconds": "5"}

    def test_mixed_style(self):
        """--params max_items=5 cooldown_seconds=5 --params max_concurrency=1"""
        result = self._parse_params(["--params", "max_items=5", "cooldown_seconds=5", "--params", "max_concurrency=1"])
        assert result == {"max_items": "5", "cooldown_seconds": "5", "max_concurrency": "1"}

    def test_single_param(self):
        """--params projectCode=ABC"""
        result = self._parse_params(["--params", "projectCode=ABC"])
        assert result == {"projectCode": "ABC"}

    def test_no_params(self):
        """No --params at all."""
        result = self._parse_params([])
        assert result == {}

    def test_value_with_equals(self):
        """--params key=val=ue (value contains =)"""
        result = self._parse_params(["--params", "key=val=ue"])
        assert result == {"key": "val=ue"}

    def test_empty_value(self):
        """--params key= (empty value)"""
        result = self._parse_params(["--params", "key="])
        assert result == {"key": ""}

    def test_later_value_overrides(self):
        """--params key=1 --params key=2 (last wins)"""
        result = self._parse_params(["--params", "key=1", "--params", "key=2"])
        assert result == {"key": "2"}
