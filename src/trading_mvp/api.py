from fastapi import FastAPI

from .broker import InMemoryBroker
from .models import SystemState
from .trading.application.strategy import MomentumStrategy
from .trading.domain.market_data import Candle
from pydantic import BaseModel
from .risk import RiskPolicy
from .service import TradingService
from .bootstrap import build_broker_lab

app = FastAPI(title="AI Trading MVP", version="0.1.0")
service = TradingService(InMemoryBroker(), RiskPolicy())
broker_lab = build_broker_lab()
strategy = MomentumStrategy()


class CandlePayload(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@app.get("/health")
def health():
    return {"state": service.state.value, "mode": "DEMO"}


@app.post("/control/pause")
def pause():
    service.pause()
    return {"state": service.state.value}


@app.post("/control/resume")
def resume():
    service.resume()
    return {"state": service.state.value}


@app.post("/control/close-all")
def close_all():
    service.state = SystemState.CLOSE_ALL_IN_PROGRESS
    closed = service.broker.close_all()
    service.state = SystemState.PAUSED
    return {"state": service.state.value, "closed": closed}


@app.post("/broker/connect")
def broker_connect():
    return {"status": broker_lab.connect()}


@app.get("/broker/reconcile")
def broker_reconcile():
    return {"positions": [position.model_dump() for position in broker_lab.reconcile()]}


@app.post("/broker/close-all")
def broker_close_all():
    return {"closed": broker_lab.close_all()}


@app.post("/strategy/evaluate")
def evaluate_strategy(candles: list[CandlePayload]):
    signal = strategy.evaluate([Candle(**candle.model_dump()) for candle in candles])
    return signal.__dict__
