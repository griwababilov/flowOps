from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Notification:
        notification = Notification(**kwargs)
        db.add(notification)
        return notification

    @staticmethod
    def get_by_id(db: Session, notification_id: int) -> Notification | None:
        return db.query(Notification).filter(Notification.id == notification_id).first()

    @staticmethod
    def get_by_event_id(db: Session, event_id: str) -> Notification | None:
        return db.query(Notification).filter(Notification.event_id == event_id).first()

    @staticmethod
    def get_all(db: Session) -> list[Notification]:
        return db.query(Notification).all()

    @staticmethod
    def mark_as_read(db: Session, notification: Notification) -> None:
        notification.is_read = True

    @staticmethod
    def delete(db: Session, notification: Notification) -> None:
        db.delete(notification)
