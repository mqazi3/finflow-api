from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.money import Money, MoneyIn


class AccountCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    account_type: str = Field(min_length=2, max_length=50)
    balance: MoneyIn = Decimal("0")


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    account_type: str
    balance: Money
    created_at: datetime
