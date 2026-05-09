from datetime import date

from app.schemas.analytics import MerchantSummaryResponse

from sqlalchemy import extract
from app.schemas.analytics import MonthlySummaryResponse

from sqlalchemy import func
from app.schemas.analytics import CategorySummaryResponse

import json
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.account import Account
from app.schemas.analytics import TransactionAnalyticsResponse
from app.cache import redis_client


def get_transaction_analytics(db: Session, user_id: int):
    cache_key = f"analytics:user:{user_id}"

    cached_data = redis_client.get(cache_key)

    if cached_data:
        return TransactionAnalyticsResponse(
            **json.loads(cached_data)
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .all()
    )

    total_transactions = len(transactions)

    total_deposits = sum(
        t.amount for t in transactions if t.amount > 0
    )

    total_withdrawals = sum(
        abs(t.amount) for t in transactions if t.amount < 0
    )

    current_balance = sum(
        account.balance for account in accounts
    )

    flagged_transactions = len(
        [t for t in transactions if t.is_flagged]
    )

    analytics = TransactionAnalyticsResponse(
        total_transactions=total_transactions,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        current_balance=current_balance,
        flagged_transactions=flagged_transactions,
    )

    redis_client.setex(
        cache_key,
        60,
        analytics.model_dump_json()
    )

    return analytics

def get_category_summary(db: Session, user_id: int):
    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("transaction_count")
        )
        .filter(Transaction.user_id == user_id)
        .group_by(Transaction.category)
        .all()
    )

    return [
        CategorySummaryResponse(
            category=row.category,
            total_amount=round(float(row.total_amount), 2),
            transaction_count=row.transaction_count
        )
        for row in results
    ]

def get_monthly_summary(
    db: Session,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None
):
    query = db.query(
        extract("year", Transaction.created_at).label("year"),
        extract("month", Transaction.created_at).label("month"),
        func.sum(Transaction.amount).label("total_amount"),
        func.count(Transaction.id).label("transaction_count")
    ).filter(Transaction.user_id == user_id)

    if start_date:
        query = query.filter(Transaction.created_at >= start_date)

    if end_date:
        query = query.filter(Transaction.created_at <= end_date)

    results = (
        query
        .group_by(
            extract("year", Transaction.created_at),
            extract("month", Transaction.created_at)
        )
        .order_by(
            extract("year", Transaction.created_at),
            extract("month", Transaction.created_at)
        )
        .all()
    )

    return [
        MonthlySummaryResponse(
            month=f"{int(row.year)}-{int(row.month):02d}",
            total_amount=round(float(row.total_amount), 2),
            transaction_count=row.transaction_count
        )
        for row in results
    ]

from app.schemas.analytics import MerchantSummaryResponse


def get_merchant_summary(db: Session, user_id: int):
    results = (
        db.query(
            Transaction.merchant,
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("transaction_count")
        )
        .filter(Transaction.user_id == user_id)
        .group_by(Transaction.merchant)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return [
        MerchantSummaryResponse(
            merchant=row.merchant,
            total_amount=round(float(row.total_amount), 2),
            transaction_count=row.transaction_count
        )
        for row in results
    ]

def get_top_spending_merchants(db: Session, user_id: int, limit: int = 5):
    results = (
        db.query(
            Transaction.merchant,
            func.sum(Transaction.amount).label("total_spent"),
            func.count(Transaction.id).label("transaction_count")
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.category == "Expense"
        )
        .group_by(Transaction.merchant)
        .order_by(func.sum(Transaction.amount).asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "merchant": row.merchant,
            "total_spent": round(float(row.total_spent), 2),
            "transaction_count": row.transaction_count
        }
        for row in results
    ]