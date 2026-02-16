from __future__ import annotations

import os
import time
import uuid
from typing import Any

from flask import Flask, jsonify, request


def _env_flag(name: str) -> bool:
    return os.getenv(name, "false").lower() in {"1", "true", "yes"}


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.post("/reserve")
    def reserve() -> Any:
        payload = request.get_json(silent=True) or {}
        required = ("order_id", "item_id", "quantity")
        missing = [field for field in required if field not in payload]
        if missing:
            return (
                jsonify({"status": "error", "message": "missing fields", "fields": missing}),
                400,
            )

        delay_ms = int(os.getenv("INVENTORY_DELAY_MS", "0"))
        if delay_ms > 0:
            time.sleep(delay_ms / 1000)

        if _env_flag("INVENTORY_FAIL"):
            return jsonify({"status": "error", "message": "inventory failure injected"}), 500

        reservation_id = str(uuid.uuid4())
        return (
            jsonify(
                {
                    "status": "reserved",
                    "reservation_id": reservation_id,
                    "order_id": payload["order_id"],
                }
            ),
            200,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
