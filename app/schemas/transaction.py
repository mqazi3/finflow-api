from datetime import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    account_id: int
    amount: float
    merchant: str
    category: str
    description: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": 1,
                "amount": 84.73,
                "merchant": "Amazon",
                "category": "Expense",
                "description": "Office supplies and cables"
            }
        }


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    amount: float
    merchant: str
    category: str
    description: str | None = None
    is_flagged: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    amount: float
    merchant: str
    category: str
    description: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 95.50,
                "merchant": "Target",
                "category": "Expense",
                "description": "Household supplies"
            }
        }