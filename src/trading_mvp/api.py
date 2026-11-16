from fastapi import FastAPI

from .broker import InMemoryBroker
from .models import SystemState
from .risk import RiskPolicy
from .service import TradingService

app = FastAPI(title="AI Trading MVP", version="0.1.0")
service = TradingService(InMemoryBroker(), RiskPolicy())


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
