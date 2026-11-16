from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SystemState(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CLOSE_ALL_IN_PROGRESS = "CLOSE_ALL_IN_PROGRESS"
    RECOVERING = "RECOVERING"
    FAULTED = "FAULTED"


class OrderRequest(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    entry: float = Field(gt=0)
    stop_loss: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_stop(self):
        if self.side == "BUY" and self.stop_loss >= self.entry:
            raise ValueError("BUY stop loss must be below entry")
        if self.side == "SELL" and self.stop_loss <= self.entry:
            raise ValueError("SELL stop loss must be above entry")
        return self


class Position(BaseModel):
    id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    entry: float = Field(gt=0)
    stop_loss: float = Field(gt=0)


class AccountSnapshot(BaseModel):
    equity: float = Field(ge=0)
    daily_loss: float = Field(ge=0)
    drawdown: float = Field(ge=0)
    open_risk: float = Field(ge=0)


class AuditEvent(BaseModel):
    action: str
    detail: str


class RiskDecision(BaseModel):
    allowed: bool
    reason: str
