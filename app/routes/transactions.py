from app.models.account import Account

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate
)
from app.services.transaction_service import create_transaction

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )

    if category:
        query = query.filter(Transaction.category == category)

    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Transaction.merchant.ilike(search_pattern)) |
            (Transaction.category.ilike(search_pattern))
        )

    transactions = (
        query
        .order_by(Transaction.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return transactions

@router.get("/count")
def get_transaction_count(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )

    if category:
        query = query.filter(Transaction.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Transaction.merchant.ilike(search_pattern)) |
            (Transaction.category.ilike(search_pattern))
        )

    return {
        "total_transactions": query.count()
    }

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    updated_transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    account = (
        db.query(Account)
        .filter(Account.id == transaction.account_id)
        .first()
    )

    if account:
        account.balance = (
            account.balance - transaction.amount
        )

    raw_amount = abs(updated_transaction.amount)

    if updated_transaction.category.lower() == "expense":
        normalized_amount = -raw_amount
    else:
        normalized_amount = raw_amount

    transaction.amount = normalized_amount
    transaction.merchant = updated_transaction.merchant
    transaction.category = updated_transaction.category
    transaction.description = updated_transaction.description

    if account:
        account.balance = (
            account.balance + normalized_amount
        )

    db.commit()
    db.refresh(transaction)

    return transaction

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    account = (
        db.query(Account)
        .filter(Account.id == transaction.account_id)
        .first()
    )

    if account:
        account.balance = account.balance - transaction.amount

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }

@router.post("/", response_model=TransactionResponse)
def create_transaction_route(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_transaction(
        db=db,
        transaction_data=transaction,
        user_id=current_user.id
    )