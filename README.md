# AI Trading MVP

Demo-only, rule-based trading core for the BRD. The current implementation contains:

- risk checks (0.25% per trade, 3% daily loss, 5% drawdown defaults);
- pause/resume/close-all state controls;
- broker-independent in-memory adapter for deterministic tests;
- SQLite audit repository;
- minimal FastAPI operator API.

## Current MVP scope (verified 2026-11-16)

### Implemented and tested

- Order, position, account, risk-decision and system-state models.
- Risk limits: 0.25% per trade, 3% daily loss, 5% drawdown defaults.
- Mandatory stop-loss validation.
- State controls: `RUNNING`, `PAUSED`, `CLOSE_ALL_IN_PROGRESS`, `RECOVERING`, `FAULTED`.
- Pause/resume and close-all behavior.
- Automatic close-all and pause on daily-loss/drawdown breach.
- Broker abstraction with deterministic `InMemoryBroker`.
- `MT5Broker` adapter with terminal initialization, symbol selection, `order_check`, confirmed `order_send`, reconciliation, and confirmed close-all.
- SQLite audit repository.
- FastAPI endpoints: `GET /health`, `POST /control/pause`, `POST /control/resume`, `POST /control/close-all`.
- Automated verification: 7 tests passing; Python compilation passing.

### Not yet implemented

- A concrete market-data feed and the approved rule-based strategy.
- API endpoint that submits a real trading signal/order.
- Live connection to the owner's MT5 Demo account.
- News/economic calendar, AI research, Telegram, web dashboard, backtesting, learning loop, multi-symbol/account, Binance, and Live trading.

The current artifact is therefore a **safe MVP foundation**, not yet a complete autonomous trading system. The next implementation slice is market data + one deterministic strategy + a Demo-only order endpoint.

## Broker lab and architecture

The feature-first structure is under `src/trading_mvp/trading/`:

- `domain/`: models and broker port;
- `application/`: broker lab use case;
- `infrastructure/brokers/`: broker adapter boundary;
- `interfaces/http/`: external interface boundary;
- `bootstrap.py`: composition root and mode selection.

The lab defaults to the safe in-memory broker:

```powershell
python -c "from trading_mvp.bootstrap import build_broker_lab; lab=build_broker_lab(); print(lab.connect(), lab.reconcile())"
```

To select MT5 Demo explicitly, set `TRADING_BROKER=mt5`, `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`, and optionally `MT5_TERMINAL_PATH`. The API then exposes `/broker/connect`, `/broker/reconcile`, and `/broker/close-all`. No MT5 credentials are stored in the repository.

## Run

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python -m trading_mvp.main
```

Open `http://127.0.0.1:8000/docs` for the API. This is not connected to a real broker yet. MT5 integration requires confirmation of broker symbol specifications, lot step, stop level, execution mode, and demo credentials.

## MT5 Demo adapter

The adapter is implemented in `trading_mvp.broker.MT5Broker`. Install the Windows-only integration package with `python -m pip install -e ".[mt5]"`, keep the MT5 terminal installed and logged into the Demo account, then configure `MT5Config` from environment variables in the host process. Never commit the password or place it in source control. The adapter performs `initialize`, symbol selection, `order_check`, confirmed `order_send`, position reconciliation, and confirmed close-all.
