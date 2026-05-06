from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.repositories.notification_repository import NotificationRepository


class NotificationService:

    @staticmethod
    def create_notification(
        db: Session, notification_data: NotificationCreate
    ) -> NotificationResponse:
        notification = NotificationRepository.create(
            db=db, **notification_data.model_dump()
        )

        try:
            db.commit()
            db.refresh(notification)
            return NotificationResponse.model_validate(notification)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_notification(
        db: Session, notification_id: int
    ) -> NotificationResponse:
        notification = NotificationRepository.get_by_id(
            db=db, notification_id=notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
            )

        return NotificationResponse.model_validate(notification)

    @staticmethod
    def get_notifications(db: Session) -> list[NotificationResponse]:
        notifications = NotificationRepository.get_all(db=db)
        return list(map(NotificationResponse.model_validate, notifications))

    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int) -> NotificationResponse:
        notification = NotificationRepository.get_by_id(
            db=db, notification_id=notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
            )

        try:
            NotificationRepository.mark_as_read(db=db, notification=notification)
            db.commit()
            db.refresh(notification)
            return NotificationResponse.model_validate(notification)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> None:
        notification = NotificationRepository.get_by_id(
            db=db, notification_id=notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
            )

        try:
            NotificationRepository.delete(db=db, notification=notification)
            db.commit()

        except Exception:
            db.rollback()
            raise
