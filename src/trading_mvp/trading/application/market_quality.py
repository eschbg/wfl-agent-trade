from dataclasses import dataclass

from trading_mvp.trading.domain.market_data import Candle


@dataclass(frozen=True)
class MarketDataDecision:
    accepted: bool
    reason: str


@dataclass(frozen=True)
class MarketDataQualityGate:
    max_age_seconds: int = 120

    def evaluate(self, candles: list[Candle], now: int) -> MarketDataDecision:
        if not candles:
            return MarketDataDecision(False, "no candles")
        if any(current.timestamp <= previous.timestamp for previous, current in zip(candles, candles[1:])):
            return MarketDataDecision(False, "candles are not strictly ordered")
        if now - candles[-1].timestamp > self.max_age_seconds:
            return MarketDataDecision(False, "market data is stale")
        if any(candle.high < max(candle.open, candle.close) or candle.low > min(candle.open, candle.close) for candle in candles):
            return MarketDataDecision(False, "invalid candle range")
        return MarketDataDecision(True, "market data accepted")
