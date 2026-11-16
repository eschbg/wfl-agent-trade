# AI Trading MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a testable Demo-only rule-based trading core with risk enforcement, close-all safety, audit logging, and a minimal API.

**Architecture:** Domain services depend on a broker protocol, never on MT5 directly. An in-memory broker enables deterministic tests; SQLite and FastAPI are thin adapters around the domain service.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, SQLite via the standard library, pytest.

**Spec:** `docs/superpowers/specs/2026-11-16-mvp-design.md`

## Global Constraints

- Demo-only; no live trading.
- One deterministic rule-based strategy.
- 0.25% risk/trade, 3% daily loss, 5% max drawdown defaults.
- Daily-loss/drawdown breach closes all open positions and leaves the system paused.
- No order is considered successful without broker confirmation.

## Review Focus

- Entry above risk cap: reject and audit; test in `tests/test_risk.py`.
- Daily loss breach with open positions: close all and pause; test in `tests/test_trading_service.py`.
- Duplicate close-all calls: idempotent broker behavior; test in `tests/test_broker.py`.
- Malformed order size/stop loss: reject at the trust boundary; test in `tests/test_models.py`.
- Restart/reconcile behavior: never infer broker state; test in `tests/test_trading_service.py`.

### Task 1: Project and domain models

**Files:** `pyproject.toml`, `src/trading_mvp/models.py`, `tests/test_models.py`

- Write failing tests for valid order creation and rejection of non-positive quantity or missing stop loss.
- Implement Pydantic models for `SystemState`, `Signal`, `OrderRequest`, `Position`, `AccountSnapshot`, and `AuditEvent`.
- Run `pytest tests/test_models.py -q`.

### Task 2: Risk engine and broker port

**Files:** `src/trading_mvp/risk.py`, `src/trading_mvp/broker.py`, `tests/test_risk.py`, `tests/test_broker.py`

- Write failing tests for 0.25% per-trade cap, daily loss cap, drawdown cap, and idempotent close-all.
- Implement `RiskPolicy`, `RiskDecision`, `Broker`, and `InMemoryBroker` with confirmed order/close operations.
- Run targeted tests, then full `pytest -q`.

### Task 3: Trading service and audit

**Files:** `src/trading_mvp/service.py`, `src/trading_mvp/audit.py`, `tests/test_trading_service.py`

- Write failing tests for state transitions, breach-triggered close-all, pause blocking entries, and reconciliation.
- Implement `TradingService` and SQLite audit repository.
- Run targeted tests, then full `pytest -q`.

### Task 4: Minimal API and operator docs

**Files:** `src/trading_mvp/api.py`, `src/trading_mvp/main.py`, `README.md`, `tests/test_api.py`

- Write failing API tests for health, pause/resume, signal evaluation, and close-all.
- Implement FastAPI endpoints using one service instance and environment-configured database path.
- Document local setup and clearly label MT5 integration as pending broker feasibility.
- Run full `pytest -q` and `python -m compileall src`.
