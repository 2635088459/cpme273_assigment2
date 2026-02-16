import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

SERVICE_DIR = Path(__file__).resolve().parents[1] / "order_service"


def _load_module():
    module_path = SERVICE_DIR / "app.py"
    spec = importlib.util.spec_from_file_location("order_app", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


order_app = _load_module()


class DummyResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        if self._json is None:
            raise ValueError("No JSON")
        return self._json


@pytest.fixture()
def client():
    app = order_app.create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_order_success(client):
    inventory_response = DummyResponse(200, {"reservation_id": "r-1"})
    notification_response = DummyResponse(200, {"notification_id": "n-1"})
    payload = {
        "order_id": "o-1",
        "item_id": "coffee",
        "quantity": 1,
        "user_email": "student@sjsu.edu",
    }
    print("[test_order_success] input:", payload)
    print("[test_order_success] expected: status=200, json.status=ok")
    with patch.object(order_app.requests, "post", side_effect=[inventory_response, notification_response]):
        response = client.post("/order", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    print("[test_order_success] actual:", data)
    assert data["status"] == "ok"
    assert data["reservation_id"] == "r-1"
    assert data["notification_id"] == "n-1"


def test_order_inventory_timeout(client):
    payload = {
        "order_id": "o-2",
        "item_id": "tea",
        "quantity": 2,
        "user_email": "student@sjsu.edu",
    }
    print("[test_order_inventory_timeout] input:", payload)
    print("[test_order_inventory_timeout] expected: status=504, json.message=inventory timeout")
    with patch.object(order_app.requests, "post", side_effect=requests.Timeout):
        response = client.post("/order", json=payload)
    assert response.status_code == 504
    print("[test_order_inventory_timeout] actual:", response.get_json())


def test_order_missing_fields(client):
    payload = {"order_id": "o-3"}
    print("[test_order_missing_fields] input:", payload)
    print("[test_order_missing_fields] expected: status=400, json.status=error")
    response = client.post("/order", json=payload)
    assert response.status_code == 400
    print("[test_order_missing_fields] actual:", response.get_json())


def test_order_inventory_failure(client):
    inventory_response = DummyResponse(500, {"status": "error"})
    payload = {
        "order_id": "o-4",
        "item_id": "sandwich",
        "quantity": 1,
        "user_email": "student@sjsu.edu",
    }
    print("[test_order_inventory_failure] input:", payload)
    print("[test_order_inventory_failure] expected: status=502, json.message=inventory failure")
    with patch.object(order_app.requests, "post", return_value=inventory_response):
        response = client.post("/order", json=payload)
    assert response.status_code == 502
    print("[test_order_inventory_failure] actual:", response.get_json())
