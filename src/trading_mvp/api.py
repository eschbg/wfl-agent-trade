import importlib.util
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .broker import InMemoryBroker, MT5Broker, MT5Config
from .models import SystemState
from .trading.application.strategy import MomentumStrategy
from .trading.application.backtest import MomentumBacktester
from .trading.application.market_quality import MarketDataQualityGate
from .trading.domain.market_data import Candle
from pydantic import BaseModel
from .risk import RiskPolicy
from .service import TradingService
from .bootstrap import build_broker_lab
from .audit import AuditRepository

app = FastAPI(title="AI Trading MVP", version="0.1.0")
audit = AuditRepository(":memory:")
service = TradingService(InMemoryBroker(), RiskPolicy(), audit)
broker_lab = build_broker_lab()
strategy = MomentumStrategy()


class CandlePayload(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketValidationPayload(BaseModel):
    candles: list[CandlePayload]
    now: int


class BacktestPayload(BaseModel):
    candles: list[CandlePayload]
    cost_per_trade: float = 0.0


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


@app.post("/control/recover")
def recover():
    positions = service.recover()
    return {"state": service.state.value, "positions": [position.model_dump() for position in positions]}


@app.post("/broker/connect")
def broker_connect():
    return {"status": broker_lab.connect()}


@app.get("/broker/reconcile")
def broker_reconcile():
    return {"positions": [position.model_dump() for position in broker_lab.reconcile()]}


@app.post("/broker/close-all")
def broker_close_all():
    return {"closed": broker_lab.close_all()}


BROKER_LAB_RESULT = {"state": "not_tested", "detail": "Run a read-only connection test when MT5 terminal is available."}


def _local_env() -> dict[str, str]:
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return {}
    values = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


@app.get("/broker/lab/status")
def broker_lab_status():
    env = _local_env()
    terminal = env.get("MT5_TERMINAL_PATH", "")
    return {
        "mode": env.get("TRADING_BROKER", "fake"),
        "credentials": {"login_configured": bool(env.get("MT5_LOGIN")), "secret_configured": bool(env.get("MT5_PASSWORD")), "server_configured": bool(env.get("MT5_SERVER"))},
        "terminal": {"configured": bool(terminal), "available": Path(terminal).is_file() if terminal else False},
        "connector": {"python_package_available": importlib.util.find_spec("MetaTrader5") is not None},
        "last_connection": BROKER_LAB_RESULT,
    }


@app.get("/broker/lab", response_class=HTMLResponse)
def broker_lab_page():
    return HTMLResponse(BROKER_LAB_TEMPLATE.read_text(encoding="utf-8"))


@app.post("/broker/lab/test-connection")
def test_broker_connection():
    global BROKER_LAB_RESULT
    env = _local_env()
    terminal = env.get("MT5_TERMINAL_PATH", "")
    required = ("MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER")
    if env.get("TRADING_BROKER", "fake").lower() != "mt5":
        BROKER_LAB_RESULT = {"state": "not_configured", "detail": "Set TRADING_BROKER=mt5 in .env."}
    elif any(not env.get(key) for key in required):
        BROKER_LAB_RESULT = {"state": "incomplete_config", "detail": "MT5 login, password, and server must be configured."}
    elif terminal and not Path(terminal).is_file():
        BROKER_LAB_RESULT = {"state": "terminal_missing", "detail": "Configured MT5 terminal path does not exist."}
    else:
        try:
            MT5Broker(MT5Config(login=int(env["MT5_LOGIN"]), password=env["MT5_PASSWORD"], server=env["MT5_SERVER"], terminal_path=terminal or None)).connect()
            BROKER_LAB_RESULT = {"state": "connected", "detail": "Read-only MT5 Demo connection established."}
        except Exception as exc:
            BROKER_LAB_RESULT = {"state": "connection_failed", "detail": str(exc)}
    return {"last_connection": BROKER_LAB_RESULT}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(DASHBOARD_TEMPLATE.read_text(encoding="utf-8"))


@app.get("/dashboard/state")
def dashboard_state():
    positions = broker_lab.reconcile()
    return {"state": service.state.value, "broker_mode": "fake", "equity": 0, "pnl": 0, "risk": {"open": 0, "daily_loss": 0, "drawdown": 0}, "positions": [position.model_dump() for position in positions]}


@app.get("/dashboard/audit")
def dashboard_audit():
    return {"events": audit.list_recent()}


DASHBOARD_TEMPLATE = Path(__file__).with_name("dashboard.html")
BROKER_LAB_TEMPLATE = Path(__file__).with_name("broker_lab.html")


DASHBOARD_HTML = """<!doctype html><html><head><meta charset='utf-8'><title>Trading MVP Dashboard</title><style>body{font:14px system-ui;max-width:1000px;margin:30px auto;background:#f5f7fb;color:#172033}section{background:white;border:1px solid #dfe4ee;border-radius:10px;padding:16px;margin:12px 0}button{padding:8px 12px;margin-right:8px;cursor:pointer}table{width:100%;border-collapse:collapse}td,th{padding:7px;border-bottom:1px solid #eee;text-align:left}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.metric{font-size:22px;font-weight:600}</style></head><body><h1>Trading MVP Dashboard</h1><section><div class='grid'><div>State<div id='state' class='metric'>-</div></div><div>Broker<div id='broker' class='metric'>-</div></div><div>Equity<div id='equity' class='metric'>-</div></div><div>PnL<div id='pnl' class='metric'>-</div></div></div></section><section><button onclick="post('/control/pause')">Pause</button><button onclick="post('/control/resume')">Resume</button><button onclick="post('/control/close-all')">Close All</button><span id='message'></span></section><section><h2>Positions</h2><table><thead><tr><th>ID</th><th>Symbol</th><th>Side</th><th>Qty</th><th>Entry</th><th>SL</th></tr></thead><tbody id='positions'></tbody></table></section><section><h2>Audit log</h2><pre id='audit'>Loading...</pre></section><script>async function post(path){const r=await fetch(path,{method:'POST'});document.getElementById('message').textContent=JSON.stringify(await r.json());load()}async function load(){const s=await (await fetch('/dashboard/state')).json();for(const k of ['state','broker','equity','pnl'])document.getElementById(k).textContent=k==='broker'?s.broker_mode:s[k];document.getElementById('positions').innerHTML=s.positions.map(p=>`<tr><td>${p.id}</td><td>${p.symbol}</td><td>${p.side}</td><td>${p.quantity}</td><td>${p.entry}</td><td>${p.stop_loss}</td></tr>`).join('')||'<tr><td colspan=6>No positions</td></tr>';const a=await (await fetch('/dashboard/audit')).json();document.getElementById('audit').textContent=JSON.stringify(a.events,null,2)}load();setInterval(load,5000)</script></body></html>"""


@app.post("/strategy/evaluate")
def evaluate_strategy(candles: list[CandlePayload]):
    signal = strategy.evaluate([Candle(**candle.model_dump()) for candle in candles])
    return signal.__dict__


@app.post("/market/validate")
def validate_market_data(payload: MarketValidationPayload):
    candles = [Candle(**candle.model_dump()) for candle in payload.candles]
    return MarketDataQualityGate().evaluate(candles, payload.now).__dict__


@app.post("/backtest/momentum")
def backtest_momentum(payload: BacktestPayload):
    candles = [Candle(**candle.model_dump()) for candle in payload.candles]
    return MomentumBacktester(payload.cost_per_trade).run(candles).__dict__
