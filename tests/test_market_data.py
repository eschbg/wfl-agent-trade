from trading_mvp.trading.infrastructure.market_data import InMemoryMarketData
from trading_mvp.trading.domain.market_data import Candle


def test_market_data_returns_latest_candles_in_order():
    feed = InMemoryMarketData([Candle(timestamp=1, open=1, high=2, low=1, close=2, volume=3)])
    assert feed.latest("XAUUSD", "M1", 1)[0].close == 2
