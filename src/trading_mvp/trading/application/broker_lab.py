from dataclasses import dataclass

from trading_mvp.trading.domain.models import Position
from trading_mvp.trading.domain.ports import BrokerPort


@dataclass
class BrokerLab:
    broker: BrokerPort

    def connect(self) -> str:
        self.broker.connect()
        return "connected"

    def reconcile(self) -> list[Position]:
        return self.broker.reconcile()

    def close_all(self) -> list[str]:
        return self.broker.close_all()
