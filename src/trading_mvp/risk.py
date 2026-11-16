from dataclasses import dataclass

from .models import AccountSnapshot, OrderRequest, RiskDecision


@dataclass(frozen=True)
class RiskPolicy:
    risk_per_trade: float = 0.0025
    daily_loss_limit: float = 0.03
    max_drawdown: float = 0.05


class RiskEngine:
    def __init__(self, policy: RiskPolicy):
        self.policy = policy

    def evaluate(self, order: OrderRequest, account: AccountSnapshot) -> RiskDecision:
        if account.daily_loss >= account.equity * self.policy.daily_loss_limit:
            return RiskDecision(allowed=False, reason="daily loss limit reached")
        if account.drawdown >= account.equity * self.policy.max_drawdown:
            return RiskDecision(allowed=False, reason="max drawdown reached")
        risk = abs(order.entry - order.stop_loss) * order.quantity
        cap = account.equity * self.policy.risk_per_trade
        if risk + account.open_risk > cap:
            return RiskDecision(allowed=False, reason="trade risk exceeds cap")
        return RiskDecision(allowed=True, reason="risk checks passed")
