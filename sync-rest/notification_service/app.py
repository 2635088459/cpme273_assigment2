from __future__ import annotations

import os
import uuid
from typing import Any

from flask import Flask, jsonify, request


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.post("/send")
    def send_notification() -> Any:
        payload = request.get_json(silent=True) or {}
        required = ("order_id", "user_email")
        missing = [field for field in required if field not in payload]
        if missing:
            return (
                jsonify({"status": "error", "message": "missing fields", "fields": missing}),
                400,
            )

        notification_id = str(uuid.uuid4())
        return (
            jsonify(
                {
                    "status": "sent",
                    "notification_id": notification_id,
                    "order_id": payload["order_id"],
                }
            ),
            200,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5002"))
    app.run(host="0.0.0.0", port=port)
