from fastapi.testclient import TestClient

from trading_mvp.api import app


def test_broker_lab_status_never_exposes_password():
    response = TestClient(app).get("/broker/lab/status")
    assert response.status_code == 200
    body = response.json()
    assert {"mode", "credentials", "terminal", "connector", "last_connection"} <= body.keys()
    assert "password" not in str(body).lower()
