from types import SimpleNamespace

from trading_mvp.broker import MT5Broker, MT5Config
from trading_mvp.models import OrderRequest


class FakeMT5:
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    TRADE_ACTION_DEAL = 1
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 1
    TRADE_RETCODE_DONE = 10009

    def __init__(self):
        self.sent = []

    def initialize(self, **kwargs):
        return True

    def symbol_select(self, symbol, enabled):
        return True

    def symbol_info_tick(self, symbol):
        return SimpleNamespace(ask=2000.0, bid=1999.5)

    def order_check(self, request):
        return SimpleNamespace(retcode=0, comment="ok")

    def order_send(self, request):
        self.sent.append(request)
        return SimpleNamespace(retcode=self.TRADE_RETCODE_DONE, order=123, deal=456, price=2000.0)


def test_mt5_broker_checks_and_confirms_order():
    fake = FakeMT5()
    broker = MT5Broker(MT5Config(login=1, password="p", server="demo"), module=fake)
    broker.connect()
    position = broker.submit(OrderRequest(symbol="XAUUSD", side="BUY", quantity=0.01, entry=2000, stop_loss=1990))
    assert position.id == "123"
    assert fake.sent[0]["sl"] == 1990
