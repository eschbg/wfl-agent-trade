from trading_mvp.broker import InMemoryBroker
from trading_mvp.models import AccountSnapshot, OrderRequest, SystemState
from trading_mvp.risk import RiskPolicy
from trading_mvp.service import TradingService


def test_daily_loss_breach_closes_positions_and_pauses():
    broker = InMemoryBroker()
    service = TradingService(broker, RiskPolicy())
    service.state = SystemState.RUNNING
    broker.seed_position(symbol="XAUUSD")
    service.on_account_snapshot(AccountSnapshot(equity=10000, daily_loss=300, drawdown=0, open_risk=0))
    assert service.state is SystemState.PAUSED
    assert broker.positions == []


def test_paused_service_rejects_entry():
    service = TradingService(InMemoryBroker(), RiskPolicy())
    service.state = SystemState.PAUSED
    result = service.submit(OrderRequest(symbol="XAUUSD", side="BUY", quantity=0.01, entry=2000, stop_loss=1990), AccountSnapshot(equity=10000, daily_loss=0, drawdown=0, open_risk=0))
    assert result.allowed is False
