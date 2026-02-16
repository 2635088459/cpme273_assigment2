import importlib.util
from pathlib import Path

import pytest

SERVICE_DIR = Path(__file__).resolve().parents[1] / "inventory_service"


def _load_module():
    module_path = SERVICE_DIR / "app.py"
    spec = importlib.util.spec_from_file_location("inventory_app", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


inventory_app = _load_module()


@pytest.fixture()
def client():
    app = inventory_app.create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_reserve_success(client, monkeypatch):
    monkeypatch.setenv("INVENTORY_FAIL", "false")
    payload = {"order_id": "o-1", "item_id": "coffee", "quantity": 2}
    print("[test_reserve_success] input:", payload)
    print("[test_reserve_success] expected: status=200, json.status=reserved")
    response = client.post("/reserve", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    print("[test_reserve_success] actual:", data)
    assert data["status"] == "reserved"
    assert data["reservation_id"]


def test_reserve_failure(client, monkeypatch):
    monkeypatch.setenv("INVENTORY_FAIL", "true")
    payload = {"order_id": "o-2", "item_id": "bagel", "quantity": 1}
    print("[test_reserve_failure] input:", payload)
    print("[test_reserve_failure] expected: status=500, json.status=error")
    response = client.post("/reserve", json=payload)
    assert response.status_code == 500
    print("[test_reserve_failure] actual:", response.get_json())


def test_reserve_missing_fields(client):
    payload = {"order_id": "o-3"}
    print("[test_reserve_missing_fields] input:", payload)
    print("[test_reserve_missing_fields] expected: status=400, json.status=error")
    response = client.post("/reserve", json=payload)
    assert response.status_code == 400
    print("[test_reserve_missing_fields] actual:", response.get_json())
