from __future__ import annotations

import uuid


def _make_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def new_order_id() -> str:
    return _make_id("order")


def new_reservation_id() -> str:
    return _make_id("res")


def new_notification_id() -> str:
    return _make_id("notif")


def new_trace_id() -> str:
    return _make_id("trace")


def new_message_id() -> str:
    return _make_id("msg")
