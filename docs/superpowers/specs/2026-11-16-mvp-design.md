# AI Trading MVP Design

## Intent

Build a safe Demo-only trading core for one rule-based strategy on XAUUSD/MT5. The core must make every entry pass risk checks, support owner pause/close-all behavior, recover by reconciling broker state, and retain an audit trail.

## Goals

- deterministic signal and risk domain APIs;
- broker-independent execution port with an in-memory adapter for tests;
- SQLite audit persistence;
- minimal FastAPI control surface;
- explicit safety states: `RUNNING`, `PAUSED`, `CLOSE_ALL_IN_PROGRESS`, `RECOVERING`, `FAULTED`.

## Non-goals

AI/news in the order path, live trading, multi-broker, multi-symbol, advanced charts, adaptive learning, and Telegram control are deferred.

## Approach

Python + FastAPI + SQLite is selected over an MQL5-only implementation because the risk, audit, and control domain remains reusable when Binance or additional brokers are added. A React dashboard is deferred because it adds scope without improving the first safety gate.

## Safety decisions

- Demo risk per trade defaults to 0.25% of equity.
- Daily loss limit defaults to 3%; max drawdown defaults to 5%.
- A daily-loss or drawdown breach locks new entries and closes all open positions before remaining paused.
- Broker execution is behind a protocol; no production code assumes an order was accepted without broker confirmation.

## Open integration boundary

The MT5 adapter is a later integration task because broker name, symbol contract, lot step, stop level, and execution behavior are not yet known. The first MVP remains executable with a deterministic fake broker.

## Verified implementation status (2026-11-16)

Implemented: domain models, risk engine, safety states, pause/resume/close-all, automatic breach response, in-memory broker, MT5 adapter, SQLite audit repository, minimal FastAPI control endpoints, and automated tests.

Not implemented: concrete market-data source, approved trading strategy, real Demo-account connection, order-submission API, news/AI research, Telegram, dashboard, backtesting, learning loop, multi-broker/product support, and Live trading.

Acceptance evidence: 7 automated tests pass and `python -m compileall -q src` passes. The MT5 adapter is tested with an injected fake module; it has not yet been validated against the Owner's actual terminal/account.
