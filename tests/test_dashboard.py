from fastapi.testclient import TestClient

from trading_mvp.api import app


def test_dashboard_exposes_status_positions_controls_and_audit():
    client = TestClient(app)
    assert client.get("/dashboard").status_code == 200
    state = client.get("/dashboard/state").json()
    assert {"state", "broker_mode", "equity", "pnl", "risk", "positions"} <= state.keys()
    assert "events" in client.get("/dashboard/audit").json()
    assert client.post("/control/pause").status_code == 200
    assert client.post("/control/resume").status_code == 200
