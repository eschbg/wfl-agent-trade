from .audit import AuditRepository
from .broker import Broker
from .models import AccountSnapshot, OrderRequest, RiskDecision, SystemState
from .risk import RiskEngine, RiskPolicy


class TradingService:
    def __init__(self, broker: Broker, policy: RiskPolicy, audit: AuditRepository | None = None):
        self.broker = broker
        self.risk = RiskEngine(policy)
        self.audit = audit
        self.state = SystemState.PAUSED

    def _record(self, action: str, detail: str):
        if self.audit:
            self.audit.record(action, detail)

    def on_account_snapshot(self, account: AccountSnapshot):
        if account.daily_loss >= account.equity * self.risk.policy.daily_loss_limit or account.drawdown >= account.equity * self.risk.policy.max_drawdown:
            self.state = SystemState.CLOSE_ALL_IN_PROGRESS
            closed = self.broker.close_all()
            self._record("close_all", f"closed={closed}")
            self.state = SystemState.PAUSED

    def submit(self, order: OrderRequest, account: AccountSnapshot) -> RiskDecision:
        if self.state is not SystemState.RUNNING:
            return RiskDecision(allowed=False, reason=f"system is {self.state.value}")
        decision = self.risk.evaluate(order, account)
        self._record("risk_decision", decision.reason)
        if decision.allowed:
            self.broker.submit(order)
            self._record("order_submitted", order.model_dump_json())
        return decision

    def pause(self):
        self.state = SystemState.PAUSED
        self._record("pause", "owner pause")

    def resume(self):
        self.broker.reconcile()
        self.state = SystemState.RUNNING
        self._record("resume", "reconciled broker")
