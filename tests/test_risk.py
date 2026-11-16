from trading_mvp.broker import InMemoryBroker
from trading_mvp.models import AccountSnapshot, OrderRequest, Position
from trading_mvp.risk import RiskPolicy, RiskEngine


def test_risk_engine_rejects_order_over_quarter_percent():
    engine = RiskEngine(RiskPolicy())
    order = OrderRequest(symbol="XAUUSD", side="BUY", quantity=3, entry=2000, stop_loss=1990)
    decision = engine.evaluate(order, AccountSnapshot(equity=10000, daily_loss=0, drawdown=0, open_risk=0))
    assert decision.allowed is False


def test_close_all_is_idempotent():
    broker = InMemoryBroker()
    broker.positions.append(Position(id="p1", symbol="XAUUSD", side="BUY", quantity=1, entry=2000, stop_loss=1990))
    assert broker.close_all() == ["p1"]
    assert broker.close_all() == []
