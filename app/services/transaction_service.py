from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.cache import redis_client
from app.logger import logger
from app.models.account import Account
from app.models.transaction import Transaction


FLAG_THRESHOLD = 10000


def _normalize_amount(amount: float, category: str) -> float:
    """Expenses are stored as negative amounts; everything else as positive."""
    raw_amount = abs(amount)
    return -raw_amount if category.lower() == "expense" else raw_amount


def _invalidate_analytics_cache(user_id: int) -> None:
    """Drop cached analytics so the next request recomputes from the database.

    A Redis outage should not fail a write that already committed, so errors
    are logged instead of raised. The 60-second TTL bounds any staleness.
    """
    try:
        redis_client.delete(f"analytics:user:{user_id}")
    except Exception:
        logger.warning(f"Could not invalidate analytics cache for user {user_id}")


def _get_user_transaction(db: Session, transaction_id: int, user_id: int) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction


def _get_user_account(db: Session, account_id: int, user_id: int) -> Account | None:
    return (
        db.query(Account)
        .filter(
            Account.id == account_id,
            Account.user_id == user_id
        )
        .first()
    )


def create_transaction(db: Session, transaction_data, user_id: int):
    account = _get_user_account(db, transaction_data.account_id, user_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found for this user"
        )

    normalized_amount = _normalize_amount(
        transaction_data.amount, transaction_data.category
    )

    transaction = Transaction(
        user_id=user_id,
        account_id=transaction_data.account_id,
        amount=normalized_amount,
        merchant=transaction_data.merchant,
        category=transaction_data.category,
        description=transaction_data.description,
        is_flagged=abs(normalized_amount) > FLAG_THRESHOLD
    )

    account.balance = account.balance + normalized_amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    _invalidate_analytics_cache(user_id)

    return transaction


def update_transaction(db: Session, transaction_id: int, update_data, user_id: int):
    transaction = _get_user_transaction(db, transaction_id, user_id)
    account = _get_user_account(db, transaction.account_id, user_id)

    normalized_amount = _normalize_amount(update_data.amount, update_data.category)

    # Reverse the old amount and apply the new one in the same commit
    if account:
        account.balance = account.balance - transaction.amount + normalized_amount

    transaction.amount = normalized_amount
    transaction.merchant = update_data.merchant
    transaction.category = update_data.category
    transaction.description = update_data.description
    transaction.is_flagged = abs(normalized_amount) > FLAG_THRESHOLD

    db.commit()
    db.refresh(transaction)

    _invalidate_analytics_cache(user_id)

    return transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> None:
    transaction = _get_user_transaction(db, transaction_id, user_id)
    account = _get_user_account(db, transaction.account_id, user_id)

    if account:
        account.balance = account.balance - transaction.amount

    db.delete(transaction)
    db.commit()

    _invalidate_analytics_cache(user_id)


def get_transaction(db: Session, transaction_id: int, user_id: int) -> Transaction:
    return _get_user_transaction(db, transaction_id, user_id)
