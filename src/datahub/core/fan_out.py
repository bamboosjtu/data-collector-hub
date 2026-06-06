"""Thin plugin_handler trigger mechanism.

Core provides only the mechanism to load and invoke a plugin-declared handler.
All fan-out logic, date slicing, auto_params, and data queries belong in plugins.

Trigger config example::

    trigger:
      type: plugin_handler
      handler: <plugin_module>.<module>:<function>

Core resolves the handler, builds a context dict, and calls it.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


def load_plugin_handler(handler_path: str):
    """Load a handler function from a module:path string.

    Example: "dcp.fan_out:refresh_towers_for_current_plan_projects"
    """
    if ":" not in handler_path:
        raise ValueError(f"Invalid handler path: {handler_path!r} — expected 'module:function'")
    module_path, func_name = handler_path.rsplit(":", 1)
    import importlib
    module = importlib.import_module(f"plugins.{module_path}")
    handler = getattr(module, func_name)
    if not callable(handler):
        raise TypeError(f"Handler {handler_path!r} is not callable")
    return handler


def build_handler_context(
    *,
    store: Any,
    plugins: list,
    trigger_clients: dict[str, Any],
    ingestion_job_id: str,
    callback_base_url: str,
    params: dict[str, Any],
    command: Any,
    plugin: Any,
) -> dict[str, Any]:
    """Build the context dict passed to plugin handlers.

    This is the only contract between core and plugin handlers.
    Core does not prescribe what the handler does with it.
    """
    return {
        "store": store,
        "plugins": plugins,
        "trigger_clients": trigger_clients,
        "ingestion_job_id": ingestion_job_id,
        "callback_base_url": callback_base_url,
        "params": params,
        "command": command,
        "plugin": plugin,
    }


def run_handler_async(handler, ctx: dict[str, Any]) -> None:
    """Run a plugin handler in a background thread.

    This is the only async mechanism core provides for plugin handlers.
    """
    def _run():
        try:
            handler(ctx)
        except Exception as exc:
            logger.exception("plugin_handler async execution failed: %s", exc)
            try:
                store = ctx.get("store")
                parent_job_id = ctx.get("ingestion_job_id")
                if store and parent_job_id:
                    store.mark_job(parent_job_id, status="failed", error=str(exc))
            except Exception:
                pass

    thread = threading.Thread(target=_run, daemon=True, name=f"plugin-handler-{ctx.get('ingestion_job_id', 'unknown')}")
    thread.start()
