from datetime import datetime

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    account_type: str = Field(min_length=2, max_length=50)
    balance: float = 0


class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    account_type: str
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True