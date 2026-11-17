from trading_mvp.trading.domain.market_data import Candle
from trading_mvp.trading.application.strategy import MomentumStrategy


def candles(*closes):
    return [Candle(timestamp=i, open=value, high=value, low=value, close=value, volume=1) for i, value in enumerate(closes)]


def test_strategy_requires_enough_candles():
    signal = MomentumStrategy(min_candles=3).evaluate(candles(2000, 2001))
    assert signal.action == "NO_TRADE"


def test_strategy_emits_buy_with_stop_loss_when_momentum_rises():
    signal = MomentumStrategy(min_candles=3, stop_distance=10).evaluate(candles(2000, 2001, 2002))
    assert signal.action == "BUY"
    assert signal.entry == 2002
    assert signal.stop_loss == 1992


def test_strategy_emits_sell_with_stop_loss_when_momentum_falls():
    signal = MomentumStrategy(min_candles=3, stop_distance=10).evaluate(candles(2002, 2001, 2000))
    assert signal.action == "SELL"
    assert signal.stop_loss == 2010
