from pydantic import BaseModel

from app.schemas.money import Money


class TransactionAnalyticsResponse(BaseModel):
    total_transactions: int
    total_deposits: Money
    total_withdrawals: Money
    current_balance: Money
    flagged_transactions: int = 0


class CategorySummaryResponse(BaseModel):
    category: str
    total_amount: Money
    transaction_count: int


class MonthlySummaryResponse(BaseModel):
    month: str
    total_amount: Money
    transaction_count: int


class MerchantSummaryResponse(BaseModel):
    merchant: str
    total_amount: Money
    transaction_count: int


class TopMerchantResponse(BaseModel):
    merchant: str
    total_spent: Money
    transaction_count: int
