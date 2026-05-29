from __future__ import annotations

from typing import Any


def classify(existing_message: dict[str, Any] | None, existing_idempotency: dict[str, Any] | None, payload: dict[str, Any]) -> str:
    if existing_idempotency and existing_idempotency["message_id"] != payload["message_id"]:
        return "idempotency_conflict"
    if not existing_message:
        return "new"
    if existing_message["payload_hash"] != payload["payload_hash"]:
        return "payload_hash_conflict"
    if existing_message["status"] == "succeeded":
        return "duplicate_accepted"
    return "retry"
