# Architecture Consensus: Prioritization & Safety Sequence

**Date**: 2026-11-17  
**Participants**: Antigravity & Codex Reviewers  
**Subject**: WFL Trading MVP Pre-Demo Architecture Consensus  

---

## Consensus Agreement

We fully concur with the prioritization sequence:

1. **Gate A: Instrument Specifications & Contract-Aware Risk Sizing**
   - Introduce `SymbolSpec` (`contract_size`, `volume_step`, `min_volume`, `max_volume`, `tick_size`, `tick_value`).
   - Fix the 100x risk underestimation in `RiskEngine` by factoring in contract size for Gold (XAUUSD, 100 oz/lot) and CFDs.
   - Introduce `PositionSizer` to deterministically calculate safe lot sizes rounded to broker `volume_step`.

2. **Gate B: Single-Broker Composition Root**
   - Eliminate the split-brain architecture where `TradingService` is hardcoded to `InMemoryBroker` while `broker_lab` and `/dashboard/state` query an independent broker instance.
   - Route all API endpoints, operator controls (`/control/close-all`, `/control/resume`), and dashboard state through a single broker instance provided by `bootstrap.py`.

3. **Subsequent Step: MT5 Adapter Hardening**
   - Once Gates A & B pass, harden `MT5Broker`: dynamic filling mode negotiation (`FOK`/`IOC`/`RETURN`), safe tick `None` handling, non-aborting partial liquidation in `close_all()`, and real `account_info()` ingestion.

4. **Deferred Items**
   - Market dashboard enrichment, AI/news integration, and Demo submit endpoints remain strictly deferred until Gates A & B and MT5 adapter hardening are fully verified with passing unit tests.

---

## Immediate Implementation Slice

- **Files to update**: `src/trading_mvp/models.py`, `src/trading_mvp/risk.py`, `src/trading_mvp/bootstrap.py`, `src/trading_mvp/api.py`.
- **Target tests**: `tests/test_risk.py`, `tests/test_trading_service.py`, and a new test validating unified broker state.
