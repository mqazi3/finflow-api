from pydantic import BaseModel


class TransactionAnalyticsResponse(BaseModel):
    total_transactions: int
    total_deposits: float
    total_withdrawals: float
    current_balance: float
    flagged_transactions: int = 0


class CategorySummaryResponse(BaseModel):
    category: str
    total_amount: float
    transaction_count: int


class MonthlySummaryResponse(BaseModel):
    month: str
    total_amount: float
    transaction_count: int


class MerchantSummaryResponse(BaseModel):
    merchant: str
    total_amount: float
    transaction_count: int


class TopMerchantResponse(BaseModel):
    merchant: str
    total_spent: float
    transaction_count: int
