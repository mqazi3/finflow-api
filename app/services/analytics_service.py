import json
from datetime import date, timedelta

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.cache import redis_client
from app.logger import logger
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.analytics import (
    CategorySummaryResponse,
    MerchantSummaryResponse,
    MonthlySummaryResponse,
    TopMerchantResponse,
    TransactionAnalyticsResponse,
)


ANALYTICS_CACHE_TTL_SECONDS = 60


def get_transaction_analytics(db: Session, user_id: int):
    cache_key = f"analytics:user:{user_id}"

    # If Redis is down, fall back to the database instead of failing the request
    try:
        cached_data = redis_client.get(cache_key)
    except Exception:
        logger.warning("Redis unavailable; computing analytics from the database")
        cached_data = None

    if cached_data:
        return TransactionAnalyticsResponse(**json.loads(cached_data))

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

    analytics = TransactionAnalyticsResponse(
        total_transactions=len(transactions),
        total_deposits=sum(t.amount for t in transactions if t.amount > 0),
        total_withdrawals=sum(abs(t.amount) for t in transactions if t.amount < 0),
        current_balance=sum(account.balance for account in accounts),
        flagged_transactions=sum(1 for t in transactions if t.is_flagged),
    )

    try:
        redis_client.setex(
            cache_key,
            ANALYTICS_CACHE_TTL_SECONDS,
            analytics.model_dump_json()
        )
    except Exception:
        logger.warning("Redis unavailable; analytics result not cached")

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
        # created_at is a timestamp, so "<= end_date" would stop at midnight and
        # drop the rest of that day. Compare against the start of the next day.
        query = query.filter(Transaction.created_at < end_date + timedelta(days=1))

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
    # Expenses are stored as negative amounts, so the most negative sum is the
    # biggest spend. Match the category case-insensitively, the same way
    # transaction creation decides whether an amount is an expense.
    results = (
        db.query(
            Transaction.merchant,
            func.sum(Transaction.amount).label("total_spent"),
            func.count(Transaction.id).label("transaction_count")
        )
        .filter(
            Transaction.user_id == user_id,
            func.lower(Transaction.category) == "expense"
        )
        .group_by(Transaction.merchant)
        .order_by(func.sum(Transaction.amount).asc())
        .limit(limit)
        .all()
    )

    return [
        TopMerchantResponse(
            merchant=row.merchant,
            total_spent=round(abs(float(row.total_spent)), 2),
            transaction_count=row.transaction_count
        )
        for row in results
    ]
