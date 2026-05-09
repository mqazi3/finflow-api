from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import create_account, get_accounts

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@router.post("/", response_model=AccountResponse)
def create_account_route(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_account(db, account, current_user.id)


@router.get("/", response_model=List[AccountResponse])
def get_accounts_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_accounts(db, current_user.id)