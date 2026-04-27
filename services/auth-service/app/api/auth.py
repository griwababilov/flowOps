from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserOut,
    Token,
    TokenPair,
    RefreshRequest,
    LogoutRequest,
)

from app.services.auth_service import AuthService
from app.utils.dependencies import get_db
from app.utils.dependencies import get_db, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register(
        db,
        email=payload.email,
        username=payload.username,
        password=payload.password,
    )


@router.get("/validate")
def validate(current_user = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "role": current_user.role,
        #"is_superuser": current_user.is_superuser,
    }


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login(
        db,
        email=payload.email,
        password=payload.password,
    )

@router.get("/me", response_model=UserOut)
def me(current_user = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService.refresh(db, refresh_token=payload.refresh_token)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    return AuthService.logout(db, refresh_token=payload.refresh_token)
