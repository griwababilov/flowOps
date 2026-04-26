from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.repositories.user_repository import UserRepository


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
        
        token = create_access_token(subject=str(user.id))
        
        return {"access_token": token}