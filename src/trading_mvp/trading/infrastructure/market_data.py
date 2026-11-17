from typing import Any

from trading_mvp.trading.domain.market_data import Candle


class InMemoryMarketData:
    def __init__(self, candles: list[Candle]):
        self.candles = candles

    def latest(self, symbol: str, timeframe: str, limit: int) -> list[Candle]:
        return self.candles[-limit:]


class MT5MarketData:
    def __init__(self, mt5: Any, timeframe: int):
        self.mt5 = mt5
        self.timeframe = timeframe

    def latest(self, symbol: str, timeframe: str, limit: int) -> list[Candle]:
        rates = self.mt5.copy_rates_from_pos(symbol, self.timeframe, 0, limit)
        if rates is None:
            raise RuntimeError(f"MT5 market data failed: {self.mt5.last_error()}")
        return [Candle(int(row["time"]), float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]), float(row["tick_volume"])) for row in rates]
