# Demo Execution Readiness Plan

**Goal:** Bring the current fake-broker MVP to a safe, observable MT5 Demo execution candidate once a local MT5 terminal is available.

**Status:** Planning only. `MT5_TERMINAL_PATH` is currently unavailable; no Demo order execution is enabled.

## Evidence used

- Current suite: 21 automated tests pass.
- Broker Lab confirms configured account fields and Python connector, but terminal executable is missing.
- Antigravity CLI review identified MT5 adapter failure modes: `order_check` can be `None`, tick data can be unavailable, a failed close currently aborts subsequent closes, and hard-coded IOC filling can be incompatible with a broker.

## P0 — must complete before Demo order submission

### 0. Eliminate unsafe local wiring before terminal work

Use one broker instance for the service, dashboard, and emergency controls; do not let `TradingService` hold an in-memory broker while broker endpoints use MT5. Persist audit events with UTC timestamps and make close-all transition to `FAULTED` if unresolved positions remain.

**Acceptance:** one integration test proves `/control/close-all` and broker reconciliation use the identical broker state; injected close failure produces `FAULTED`, an audit event, and a list of unresolved tickets.

### 1. Broker capability discovery

Read and persist symbol/account capabilities on startup: symbol visibility, trade mode, min/max/step volume, contract size, tick size/value, stop/freeze level, execution mode, supported filling modes, margin and spread.

**Acceptance:** a Demo-only diagnostics report is populated from the broker; unsupported XAUUSD conditions block entry with an auditable reason.

### 2. Correct money and risk calculation

Replace price-distance × quantity sizing with broker instrument math using tick value/size and volume step. Separate `risk_per_trade` from `max_total_open_risk`; define daily reset timezone and reference equity.

**Acceptance:** contract fixtures cover volume rounding, min-lot rejection, total-risk cap, spread/cost inclusion, and known XAUUSD examples.

### 3. Harden MT5 request/response handling

Require successful `symbol_info_tick`, `order_check`, and `order_send` results. Select filling mode from broker capabilities. Add client request IDs/idempotency and retain every request/result/retcode.

**Acceptance:** simulated missing tick, `None` check result, reject retcode, timeout, and duplicate request cannot create an untracked or duplicate position.

### 4. Position lifecycle and emergency close-all

Persist order/pending/filled/rejected/partial/closed states, broker ticket, SL/TP confirmation, costs, slippage, and close reason. Attempt every close independently; report unresolved tickets and leave the system paused/faulted.

**Acceptance:** one failing close does not prevent attempts on remaining positions; Close All cannot report success while positions or pending orders remain.

## P1 — Demo validation and resilience

### 5. Reconciliation and fault recovery

On startup/disconnect, move to `RECOVERING`, fetch account/orders/positions/history, resolve unknown request state, audit differences, then require explicit Owner Resume.

**Acceptance:** restart and simulated disconnect tests prove no new entry until reconciliation completes and no position is silently forgotten.

### 6. Strategy validation pipeline

Version strategy/data/configuration. Run backtest with broker-specific spread, commission, slippage and out-of-sample windows. Define Demo Go/No-Go KPI before a live feed trial.

**Acceptance:** report includes sample count, expectancy, drawdown, costs, sensitivity and limitations; changing a strategy/risk parameter invalidates prior validation.

### 7. Demo observability

Feed broker account/position/risk/execution data into dashboard, including signal rationale and audit trail. Retain the existing lab as an operational diagnostics page.

**Acceptance:** dashboard values reconcile to MT5 in a controlled Demo scenario; an operator can trace each position to its signal, policy decision, broker request and broker result.

## P2 — after stable Demo validation

- Telegram alerts/controlled commands with identity, confirmation and idempotency.
- Economic calendar/news as advisory context, never a direct execution dependency.
- AI research and approved strategy-change workflow.
- Multi-broker/Binance and Live-trading approval gate.

## Recommended first implementation slice

Implement `SymbolSpec` + contract-aware risk sizing + single-broker composition root first, before terminal installation. Then complete broker capability discovery after the terminal is available. This sequence removes a potential 100x XAUUSD risk error and prevents emergency controls from acting on a different broker instance; no order submission should precede it.
