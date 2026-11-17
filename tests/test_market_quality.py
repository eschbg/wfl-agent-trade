from trading_mvp.trading.domain.market_data import Candle
from trading_mvp.trading.application.market_quality import MarketDataQualityGate


def test_market_quality_rejects_stale_or_unsorted_candles():
    gate = MarketDataQualityGate(max_age_seconds=60)
    stale = [Candle(timestamp=1, open=1, high=1, low=1, close=1, volume=1)]
    unsorted = [Candle(timestamp=2, open=1, high=1, low=1, close=1, volume=1), Candle(timestamp=1, open=1, high=1, low=1, close=1, volume=1)]
    assert gate.evaluate(stale, now=100).accepted is False
    assert gate.evaluate(unsorted, now=2).accepted is False


def test_market_quality_accepts_recent_ordered_candles():
    candles = [Candle(timestamp=90, open=1, high=2, low=1, close=2, volume=1), Candle(timestamp=95, open=2, high=3, low=2, close=3, volume=1)]
    assert MarketDataQualityGate(max_age_seconds=10).evaluate(candles, now=100).accepted is True
