import pytest
from pydantic import ValidationError

from trading_mvp.models import OrderRequest


def test_order_requires_positive_quantity_and_stop_loss():
    with pytest.raises(ValidationError):
        OrderRequest(symbol="XAUUSD", side="BUY", quantity=0, entry=2000, stop_loss=None)
