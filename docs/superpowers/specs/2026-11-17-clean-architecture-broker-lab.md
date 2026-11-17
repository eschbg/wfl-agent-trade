# Clean Architecture Broker Lab Design

## Intent

Refactor the MVP into feature-first Clean Architecture and provide a broker lab that exercises connect, reconcile, submit, and close-all without requiring a real account.

## Approach

The trading feature owns domain models, risk policy, and use cases. Broker ports are defined inward-facing; in-memory and MT5 adapters live in infrastructure. FastAPI is an outer adapter. A composition root selects `fake` by default and requires explicit `mt5` configuration for Demo.

## Goals

- preserve current risk and safety behavior;
- make broker implementations swappable;
- run a deterministic lab without MT5;
- expose a small operator API for broker status, reconcile, and close-all;
- keep credentials out of source control.

## Non-goals

No live trading, strategy generation, dashboard, Telegram, Binance adapter, or broker-specific behavior in the domain.

## Proposed structure

```text
src/trading_mvp/
  trading/domain/       entities, ports, risk rules
  trading/application/  use cases
  trading/infrastructure/ brokers and persistence
  interfaces/http/      FastAPI adapter
  bootstrap.py          dependency wiring
```

Compatibility modules remain as thin imports during this refactor so existing consumers do not break abruptly.
