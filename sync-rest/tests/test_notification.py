import importlib.util
from pathlib import Path

import pytest

SERVICE_DIR = Path(__file__).resolve().parents[1] / "notification_service"


def _load_module():
    module_path = SERVICE_DIR / "app.py"
    spec = importlib.util.spec_from_file_location("notification_app", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


notification_app = _load_module()


@pytest.fixture()
def client():
    app = notification_app.create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_send_success(client):
    payload = {"order_id": "o-1", "user_email": "student@sjsu.edu"}
    print("[test_send_success] input:", payload)
    print("[test_send_success] expected: status=200, json.status=sent")
    response = client.post("/send", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    print("[test_send_success] actual:", data)
    assert data["status"] == "sent"
    assert data["notification_id"]


def test_send_missing_fields(client):
    payload = {"order_id": "o-1"}
    print("[test_send_missing_fields] input:", payload)
    print("[test_send_missing_fields] expected: status=400, json.status=error")
    response = client.post("/send", json=payload)
    assert response.status_code == 400
    print("[test_send_missing_fields] actual:", response.get_json())
