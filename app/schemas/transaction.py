from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.money import Money, MoneyIn


class TransactionCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": 1,
                "amount": 84.73,
                "merchant": "Amazon",
                "category": "Expense",
                "description": "Office supplies and cables"
            }
        }
    )

    account_id: int
    amount: MoneyIn
    merchant: str
    category: str
    description: str | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    account_id: int
    amount: Money
    merchant: str
    category: str
    description: str | None = None
    is_flagged: bool
    created_at: datetime


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 95.50,
                "merchant": "Target",
                "category": "Expense",
                "description": "Household supplies"
            }
        }
    )

    amount: MoneyIn
    merchant: str
    category: str
    description: str | None = None
