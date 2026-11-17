from trading_mvp.trading.application.backtest import MomentumBacktester
from trading_mvp.trading.domain.market_data import Candle


def test_backtest_reports_trades_and_net_return_after_costs():
    candles = [Candle(timestamp=i, open=price, high=price, low=price, close=price, volume=1) for i, price in enumerate([100, 101, 102, 101, 100, 99])]
    result = MomentumBacktester(cost_per_trade=0.1).run(candles)
    assert result.trade_count > 0
    assert isinstance(result.net_return, float)
    assert result.costs >= 0
