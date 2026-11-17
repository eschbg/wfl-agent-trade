from trading_mvp.broker import InMemoryBroker
from trading_mvp.risk import RiskPolicy
from trading_mvp.service import TradingService
from trading_mvp.models import SystemState


def test_recovery_reconciles_then_pauses_for_owner_review():
    service = TradingService(InMemoryBroker(), RiskPolicy())
    positions = service.recover()
    assert positions == []
    assert service.state is SystemState.PAUSED
