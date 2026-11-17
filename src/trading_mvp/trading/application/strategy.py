from dataclasses import dataclass

from trading_mvp.trading.domain.market_data import Candle, Signal


@dataclass(frozen=True)
class MomentumStrategy:
    min_candles: int = 3
    stop_distance: float = 10.0

    def evaluate(self, candles: list[Candle]) -> Signal:
        if len(candles) < self.min_candles:
            return Signal("NO_TRADE", None, None, "insufficient candles")
        previous, latest = candles[-2], candles[-1]
        if latest.close > previous.close:
            return Signal("BUY", latest.close, latest.close - self.stop_distance, "latest close rose")
        if latest.close < previous.close:
            return Signal("SELL", latest.close, latest.close + self.stop_distance, "latest close fell")
        return Signal("WAIT", latest.close, None, "latest close unchanged")
