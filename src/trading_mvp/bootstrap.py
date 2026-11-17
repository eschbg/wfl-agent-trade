import os

from trading_mvp.broker import InMemoryBroker, MT5Broker, MT5Config
from trading_mvp.trading.application.broker_lab import BrokerLab


def build_broker():
    mode = os.getenv("TRADING_BROKER", "fake").lower()
    if mode == "fake":
        return InMemoryBroker()
    if mode == "mt5":
        required = {key: os.getenv(key) for key in ("MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER")}
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing MT5 configuration: {', '.join(missing)}")
        return MT5Broker(MT5Config(login=int(required["MT5_LOGIN"]), password=required["MT5_PASSWORD"], server=required["MT5_SERVER"], terminal_path=os.getenv("MT5_TERMINAL_PATH")))
    raise RuntimeError(f"Unsupported TRADING_BROKER: {mode}")


def build_broker_lab() -> BrokerLab:
    return BrokerLab(build_broker())
