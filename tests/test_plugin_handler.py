"""Tests for plugin_handler loading boundary enforcement."""

from __future__ import annotations

import pytest

from src.datahub.core.fan_out import load_plugin_handler


class TestPluginHandlerBoundary:
    def test_valid_dcp_handler_loads(self):
        """dcp.fan_out handler loads successfully with plugin_name='dcp'."""
        handler = load_plugin_handler("dcp.fan_out:refresh_towers_for_current_plan_projects", plugin_name="dcp")
        assert callable(handler)

    def test_cross_plugin_handler_rejected(self):
        """Handler with prefix not matching plugin_name is rejected."""
        with pytest.raises(ValueError, match="must be scoped to plugin 'other_plugin'"):
            load_plugin_handler("dcp.fan_out:some_func", plugin_name="other_plugin")

    def test_no_plugin_name_allows_any(self):
        """Without plugin_name, any valid handler path is allowed (backward compat)."""
        # This should not raise — we're just testing the validation is skipped
        # We can't actually import a non-existent module, so we test the ValueError
        # from the prefix check is NOT raised when plugin_name is None
        # (The actual import will fail, but that's a different error)
        with pytest.raises((ImportError, ModuleNotFoundError)):
            load_plugin_handler("fake_plugin.module:func")

    def test_invalid_handler_path_format(self):
        """Handler path without colon separator is rejected."""
        with pytest.raises(ValueError, match="Invalid handler path"):
            load_plugin_handler("no_colon_here")

    def test_dcp_handler_rejected_for_wrong_plugin(self):
        """dcp handler rejected when plugin_name is not 'dcp'."""
        with pytest.raises(ValueError, match="must be scoped to plugin 'acme'"):
            load_plugin_handler("dcp.fan_out:refresh_towers_for_current_plan_projects", plugin_name="acme")
