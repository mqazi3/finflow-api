from app.cache import redis_client

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction


def create_transaction(db: Session, transaction_data, user_id: int):
    account = (
        db.query(Account)
        .filter(
            Account.id == transaction_data.account_id,
            Account.user_id == user_id
        )
        .first()
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found for this user"
        )

    raw_amount = abs(transaction_data.amount)

    if transaction_data.category.lower() == "expense":
        normalized_amount = -raw_amount
    else:
        normalized_amount = raw_amount

    is_flagged = raw_amount > 10000

    transaction = Transaction(
        user_id=user_id,
        account_id=transaction_data.account_id,
        amount=normalized_amount,
        merchant=transaction_data.merchant,
        category=transaction_data.category,
        is_flagged=is_flagged
    )

    account.balance = account.balance + normalized_amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    redis_client.delete(
        f"analytics:user:{user_id}"
    )

    return transaction


def get_all_transactions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    search: str | None = None
):
    query = db.query(Transaction).filter(
        Transaction.user_id == user_id
    )

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            (Transaction.merchant.ilike(search_pattern)) |
            (Transaction.category.ilike(search_pattern))
        )

    if sort_by == "amount":
        sort_column = Transaction.amount
    else:
        sort_column = Transaction.created_at

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.offset(skip).limit(limit).all()