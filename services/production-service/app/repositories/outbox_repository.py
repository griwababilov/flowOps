from app.models.outbox_event import OutboxEvent
from app.core.enums import OutboxEventStatus

from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from uuid import uuid4

MAX_RETRY_COUNT = 5


class OutboxRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> OutboxEvent:
        outbox_event = OutboxEvent(event_id=str(uuid4()), **kwargs)

        db.add(outbox_event)
        return outbox_event

    @staticmethod
    def claim_events_for_publish(db: Session, limit: int = 10) -> list[OutboxEvent]:
        now = datetime.now(timezone.utc)

        events = (
            db.query(OutboxEvent)
            .filter(OutboxEvent.status == OutboxEventStatus.PENDING)
            .filter(OutboxEvent.retry_count < MAX_RETRY_COUNT)
            .filter(
                or_(
                    OutboxEvent.next_retry_at.is_(None),
                    OutboxEvent.next_retry_at <= now,
                )
            )
            .filter(OutboxEvent.locked_at.is_(None))
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
            .all()
        )

        for event in events:
            event.locked_at = now
            event.status = OutboxEventStatus.PROCESSING

        return events

    @staticmethod
    def mark_as_published(outbox_event: OutboxEvent) -> None:
        outbox_event.status = OutboxEventStatus.PUBLISHED
        outbox_event.last_error = None
        outbox_event.locked_at = None
        outbox_event.next_retry_at = None
        outbox_event.published_at = datetime.now(timezone.utc)

    @staticmethod
    def mark_for_retry(outbox_event: OutboxEvent, error_message: str) -> None:
        outbox_event.status = OutboxEventStatus.PENDING
        outbox_event.last_error = error_message
        outbox_event.retry_count += 1
        outbox_event.locked_at = None
        outbox_event.next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=5)
