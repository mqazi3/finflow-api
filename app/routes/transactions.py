from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate
)
from app.services.transaction_service import (
    create_transaction,
    delete_transaction,
    get_transaction,
    update_transaction,
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


def _apply_search(query, search: Optional[str]):
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Transaction.merchant.ilike(search_pattern)) |
            (Transaction.category.ilike(search_pattern))
        )
    return query


@router.get("/", response_model=list[TransactionResponse])
def get_transactions_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
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

    query = _apply_search(query, search)

    return (
        query
        .order_by(Transaction.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/count")
def get_transaction_count_route(
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

    query = _apply_search(query, search)

    return {
        "total_transactions": query.count()
    }


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transaction(db, transaction_id, current_user.id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction_route(
    transaction_id: int,
    updated_transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_transaction(
        db=db,
        transaction_id=transaction_id,
        update_data=updated_transaction,
        user_id=current_user.id
    )


@router.delete("/{transaction_id}")
def delete_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_transaction(db, transaction_id, current_user.id)

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
