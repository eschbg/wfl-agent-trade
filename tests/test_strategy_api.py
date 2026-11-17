from fastapi.testclient import TestClient

from trading_mvp.api import app


def test_strategy_endpoint_returns_signal_without_submitting_order():
    client = TestClient(app)
    response = client.post("/strategy/evaluate", json=[
        {"timestamp": 1, "open": 2000, "high": 2001, "low": 1999, "close": 2000, "volume": 10},
        {"timestamp": 2, "open": 2000, "high": 2002, "low": 2000, "close": 2001, "volume": 11},
        {"timestamp": 3, "open": 2001, "high": 2003, "low": 2001, "close": 2002, "volume": 12},
    ])
    assert response.status_code == 200
    assert response.json()["action"] == "BUY"
