from fastapi.testclient import TestClient

from trading_mvp.api import app


def test_market_validation_backtest_and_recovery_endpoints():
    client = TestClient(app)
    candles = [{"timestamp": i, "open": 100 + i, "high": 101 + i, "low": 99 + i, "close": 100 + i, "volume": 1} for i in range(6)]
    assert client.post("/market/validate", json={"candles": candles, "now": 6}).json()["accepted"] is True
    assert "net_return" in client.post("/backtest/momentum", json={"candles": candles}).json()
    assert client.post("/control/recover").json()["state"] == "PAUSED"
