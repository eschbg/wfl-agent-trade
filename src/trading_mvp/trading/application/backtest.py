from dataclasses import dataclass

from trading_mvp.trading.domain.market_data import Candle


@dataclass(frozen=True)
class BacktestResult:
    trade_count: int
    gross_return: float
    costs: float
    net_return: float
    max_drawdown: float


@dataclass(frozen=True)
class MomentumBacktester:
    cost_per_trade: float = 0.0

    def run(self, candles: list[Candle]) -> BacktestResult:
        returns: list[float] = []
        for index in range(2, len(candles) - 1):
            direction = 1 if candles[index].close > candles[index - 1].close else -1
            returns.append((candles[index + 1].close - candles[index].close) * direction)
        gross = float(sum(returns))
        costs = len(returns) * self.cost_per_trade
        equity = peak = 0.0
        drawdown = 0.0
        for value in returns:
            equity += value - self.cost_per_trade
            peak = max(peak, equity)
            drawdown = max(drawdown, peak - equity)
        return BacktestResult(len(returns), gross, costs, gross - costs, drawdown)
