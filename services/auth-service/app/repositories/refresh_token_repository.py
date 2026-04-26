from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    @staticmethod
    def create(db: Session, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)

        return refresh_token
    
    @staticmethod
    def get_valid(db: Session, token: str) -> RefreshToken | None:
        return db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).first()
    
    @staticmethod
    def revoke(db: Session, token: str) -> None:
        refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()

        if refresh_token:
            refresh_token.is_revoked = True
            db.commit()
