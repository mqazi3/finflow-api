from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

from app.models.user import User

from app.schemas.analytics import (
    TransactionAnalyticsResponse,
    CategorySummaryResponse,
    MonthlySummaryResponse,
    MerchantSummaryResponse
)

from app.services.analytics_service import (
    get_transaction_analytics,
    get_category_summary,
    get_monthly_summary,
    get_merchant_summary,
    get_top_spending_merchants
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/transactions", response_model=TransactionAnalyticsResponse)
def get_transaction_analytics_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_transaction_analytics(db, current_user.id)

@router.get("/categories", response_model=list[CategorySummaryResponse])
def get_category_analytics_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_category_summary(
        db=db,
        user_id=current_user.id
    )

@router.get("/monthly", response_model=list[MonthlySummaryResponse])
def get_monthly_analytics_route(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_monthly_summary(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/merchants", response_model=list[MerchantSummaryResponse])
def get_merchant_analytics_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_merchant_summary(
        db=db,
        user_id=current_user.id
    )

@router.get("/top-merchants")
def get_top_merchants_route(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_top_spending_merchants(
        db=db,
        user_id=current_user.id,
        limit=limit
    )