# Clean Architecture Broker Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the MVP into feature-first Clean Architecture and add a safe fake/MT5 broker lab.

**Architecture:** Domain and application code depend only on ports. Infrastructure implements broker adapters. HTTP and bootstrap are outer adapters selected through configuration.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, pytest, optional MetaTrader5 package.

**Spec:** `docs/superpowers/specs/2026-11-17-clean-architecture-broker-lab-design.md`

## Global Constraints

- Fake broker is the default lab mode.
- MT5 mode requires explicit configuration and Demo credentials.
- No credentials in source control.
- Existing risk and safety behavior must remain intact.

## Review Focus

- Default bootstrap must never select MT5 accidentally: test configuration.
- Domain imports must not import FastAPI or MetaTrader5: test import boundary by inspection.
- Close-all must be idempotent: lab test.
- MT5 adapter errors must surface as failed operations: adapter test.
- Existing public imports must continue working: full suite.

### Task 1: Move domain and application contracts

Create feature-first domain models, broker port, risk service, and trading use case; add tests before implementation and retain compatibility imports.

### Task 2: Move broker infrastructure

Implement fake and MT5 adapters under `trading/infrastructure/brokers`, add a broker lab service, and test connect/reconcile/close-all.

### Task 3: Wire HTTP and configuration

Add bootstrap selection (`fake` default, `mt5` explicit), expose `/broker/status`, `/broker/reconcile`, and `/broker/close-all`, and preserve current controls.

### Task 4: Documentation and verification

Document lab commands, Demo environment variables, architecture boundaries, run the full test suite and compile check.
