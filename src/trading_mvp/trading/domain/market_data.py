from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Signal:
    action: str
    entry: float | None
    stop_loss: float | None
    reason: str


class MarketDataPort(Protocol):
    def latest(self, symbol: str, timeframe: str, limit: int) -> list[Candle]: ...
