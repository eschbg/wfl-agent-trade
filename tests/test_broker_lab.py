from trading_mvp.bootstrap import build_broker, build_broker_lab
from trading_mvp.broker import InMemoryBroker


def test_fake_is_the_safe_default(monkeypatch):
    monkeypatch.delenv("TRADING_BROKER", raising=False)
    assert isinstance(build_broker(), InMemoryBroker)


def test_lab_connect_reconcile_and_close_all():
    lab = build_broker_lab()
    assert lab.connect() == "connected"
    assert lab.reconcile() == []
    assert lab.close_all() == []
