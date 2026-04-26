from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.core.config import settings

from datetime import datetime, timezone, timedelta


class AuthService:

    @staticmethod
    def register(db: Session, email: str, username: str, password: str):
        if UserRepository.get_by_email(db, email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Email is already exists",
                                )
        
        if UserRepository.get_by_username(db, username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Username is already exists",
                                )
        
        return UserRepository.create(
            db=db,
            email=email,
            username=username,
            hashed_password = hash_password(password),
            )
    
    @staticmethod
    def login(db: Session, email: str, password: str):
        user = UserRepository.get_by_email(db, email)
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
                )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive",
            )
        
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        RefreshTokenRepository.create(
            db,
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    def refresh(db: Session, refresh_token: str):
        user_id = decode_token(refresh_token, expected_type="refresh")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        stored_token = RefreshTokenRepository.get_valid(db, refresh_token)

        if stored_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or revoked",
        )

        user = UserRepository.get_by_id(db, int(user_id))

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        access_token = create_access_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    @staticmethod
    def logout(db: Session, refresh_token: str):
        RefreshTokenRepository.revoke(db, refresh_token)

        return {"detail": "Logged out"}
