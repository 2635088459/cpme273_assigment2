from __future__ import annotations

import os
import uuid
from typing import Any, Dict

import requests
from flask import Flask, jsonify, request


def _get_timeout(env_name: str, default_value: float) -> float:
    raw = os.getenv(env_name, str(default_value))
    try:
        return float(raw)
    except ValueError:
        return float(default_value)


def _safe_json(response: requests.Response) -> Dict[str, Any]:
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.post("/order")
    def create_order() -> Any:
        payload = request.get_json(silent=True) or {}
        required = ("order_id", "item_id", "quantity", "user_email")
        missing = [field for field in required if field not in payload]
        if missing:
            return (
                jsonify({"status": "error", "message": "missing fields", "fields": missing}),
                400,
            )

        inventory_url = os.getenv("INVENTORY_URL", "http://inventory_service:5001/reserve")
        notification_url = os.getenv("NOTIFICATION_URL", "http://notification_service:5002/send")
        inventory_timeout = _get_timeout("INVENTORY_TIMEOUT", 1.0)
        notification_timeout = _get_timeout("NOTIFICATION_TIMEOUT", 1.0)

        inventory_payload = {
            "order_id": payload["order_id"],
            "item_id": payload["item_id"],
            "quantity": payload["quantity"],
        }

        try:
            inventory_response = requests.post(
                inventory_url,
                json=inventory_payload,
                timeout=inventory_timeout,
            )
        except requests.Timeout:
            return jsonify({"status": "error", "message": "inventory timeout"}), 504
        except requests.RequestException as exc:
            return (
                jsonify({"status": "error", "message": "inventory request failed", "detail": str(exc)}),
                502,
            )

        if inventory_response.status_code != 200:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "inventory failure",
                        "inventory_status": inventory_response.status_code,
                        "inventory_body": _safe_json(inventory_response),
                    }
                ),
                502,
            )

        reservation_id = _safe_json(inventory_response).get("reservation_id")

        notification_payload = {
            "order_id": payload["order_id"],
            "user_email": payload["user_email"],
            "reservation_id": reservation_id,
        }

        try:
            notification_response = requests.post(
                notification_url,
                json=notification_payload,
                timeout=notification_timeout,
            )
        except requests.Timeout:
            return jsonify({"status": "error", "message": "notification timeout"}), 504
        except requests.RequestException as exc:
            return (
                jsonify(
                    {"status": "error", "message": "notification request failed", "detail": str(exc)}
                ),
                502,
            )

        if notification_response.status_code != 200:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "notification failure",
                        "notification_status": notification_response.status_code,
                        "notification_body": _safe_json(notification_response),
                    }
                ),
                502,
            )

        notification_id = _safe_json(notification_response).get("notification_id")

        return (
            jsonify(
                {
                    "status": "ok",
                    "order_id": payload["order_id"],
                    "reservation_id": reservation_id,
                    "notification_id": notification_id,
                    "trace_id": str(uuid.uuid4()),
                }
            ),
            200,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
