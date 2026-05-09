from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.dependencies.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, authenticate_user


router = APIRouter(
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = create_user(db, user_data.username, user_data.password)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return user


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }