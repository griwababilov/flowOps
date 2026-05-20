from app.models.outbox_event import OutboxEvent
from app.core.enums import OutboxEventStatus

from sqlalchemy.orm import Session
from datetime import datetime, timezone


class OutboxRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> OutboxEvent:
        outbox_event = OutboxEvent(**kwargs)
        db.add(outbox_event)
        return outbox_event

    @staticmethod
    def get_events_for_publish(db: Session, limit: int = 10) -> list[OutboxEvent]:
        return (
            db.query(OutboxEvent)
            .filter(
                OutboxEvent.status.in_(
                    [OutboxEventStatus.PENDING, OutboxEventStatus.FAILED]
                )
            )
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_as_published(outbox_event: OutboxEvent) -> None:
        outbox_event.status = OutboxEventStatus.PUBLISHED
        outbox_event.published_at = datetime.now(timezone.utc)
        outbox_event.error_message = None

    @staticmethod
    def mark_as_failed(outbox_event: OutboxEvent, error_message: str) -> None:
        outbox_event.status = OutboxEventStatus.FAILED
        outbox_event.error_message = error_message
