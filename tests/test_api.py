from fastapi.testclient import TestClient

from trading_mvp.api import app


def test_health_and_pause_resume():
    client = TestClient(app)
    assert client.get("/health").json()["state"] == "PAUSED"
    assert client.post("/control/resume").json()["state"] == "RUNNING"
    assert client.post("/control/pause").json()["state"] == "PAUSED"
