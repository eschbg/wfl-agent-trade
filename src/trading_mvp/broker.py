from dataclasses import dataclass
from typing import Any, Protocol
from uuid import uuid4

from .models import OrderRequest, Position


class Broker(Protocol):
    positions: list[Position]

    def submit(self, order: OrderRequest) -> Position: ...
    def close_all(self) -> list[str]: ...
    def reconcile(self) -> list[Position]: ...


class InMemoryBroker:
    def __init__(self):
        self.positions: list[Position] = []

    def connect(self):
        return None

    def submit(self, order: OrderRequest) -> Position:
        position = Position(id=str(uuid4()), **order.model_dump())
        self.positions.append(position)
        return position

    def close_all(self) -> list[str]:
        closed = [position.id for position in self.positions]
        self.positions.clear()
        return closed

    def reconcile(self) -> list[Position]:
        return list(self.positions)

    def seed_position(self, symbol: str = "XAUUSD") -> Position:
        return self.submit(OrderRequest(symbol=symbol, side="BUY", quantity=0.01, entry=2000, stop_loss=1990))


@dataclass(frozen=True)
class MT5Config:
    login: int
    password: str
    server: str
    terminal_path: str | None = None
    deviation: int = 20
    magic: int = 260116


class MT5Broker:
    """MT5 adapter; accepts an injected module so execution can be tested safely."""

    def __init__(self, config: MT5Config, module: Any | None = None):
        self.config = config
        self.mt5 = module

    def connect(self):
        if self.mt5 is None:
            try:
                import MetaTrader5 as mt5
            except ImportError as exc:
                raise RuntimeError("Install MetaTrader5 on Windows before using MT5Broker") from exc
            self.mt5 = mt5
        kwargs = {"login": self.config.login, "password": self.config.password, "server": self.config.server}
        if not self.mt5.initialize(**kwargs) if not self.config.terminal_path else not self.mt5.initialize(self.config.terminal_path, **kwargs):
            raise RuntimeError(f"MT5 initialize failed: {self.mt5.last_error()}")

    def _ensure_connected(self):
        if self.mt5 is None:
            self.connect()

    def submit(self, order: OrderRequest) -> Position:
        self._ensure_connected()
        if not self.mt5.symbol_select(order.symbol, True):
            raise RuntimeError(f"MT5 symbol unavailable: {order.symbol}")
        tick = self.mt5.symbol_info_tick(order.symbol)
        price = tick.ask if order.side == "BUY" else tick.bid
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": order.symbol,
            "volume": order.quantity,
            "type": self.mt5.ORDER_TYPE_BUY if order.side == "BUY" else self.mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": order.stop_loss,
            "deviation": self.config.deviation,
            "magic": self.config.magic,
            "comment": "trading-mvp-demo",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        check = self.mt5.order_check(request)
        if getattr(check, "retcode", None) not in (0, None):
            raise RuntimeError(f"MT5 order_check rejected: {check}")
        result = self.mt5.order_send(request)
        if result is None or result.retcode != self.mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"MT5 order_send rejected: {result}")
        return Position(id=str(result.order), **order.model_dump())

    def reconcile(self) -> list[Position]:
        self._ensure_connected()
        raw_positions = self.mt5.positions_get() or []
        positions = []
        for raw in raw_positions:
            side = "BUY" if raw.type == self.mt5.ORDER_TYPE_BUY else "SELL"
            positions.append(Position(id=str(raw.ticket), symbol=raw.symbol, side=side, quantity=raw.volume, entry=raw.price_open, stop_loss=raw.sl or raw.price_open))
        return positions

    def close_all(self) -> list[str]:
        self._ensure_connected()
        closed = []
        for position in self.mt5.positions_get() or []:
            tick = self.mt5.symbol_info_tick(position.symbol)
            side = self.mt5.ORDER_TYPE_SELL if position.type == self.mt5.ORDER_TYPE_BUY else self.mt5.ORDER_TYPE_BUY
            price = tick.bid if position.type == self.mt5.ORDER_TYPE_BUY else tick.ask
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": side,
                "position": position.ticket,
                "price": price,
                "deviation": self.config.deviation,
                "magic": self.config.magic,
                "comment": "trading-mvp-close-all",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            result = self.mt5.order_send(request)
            if result is None or result.retcode != self.mt5.TRADE_RETCODE_DONE:
                raise RuntimeError(f"MT5 close rejected for {position.ticket}: {result}")
            closed.append(str(position.ticket))
        return closed
