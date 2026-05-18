from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.core.enums import NotificationEventType, NotificationSeverity
from app.schemas.events import (
    BaseEvent,
    PartDefectiveDetectedEvent,
    BatchCompletedEvent,
)


def handle_part_defective_detected(db: Session, payload: dict) -> NotificationResponse:

    event = PartDefectiveDetectedEvent.model_validate(payload)

    notification_data = NotificationCreate(
        event_type=event.event_type,
        title="Defective part detected",
        message=(
            f"Part {event.part_id} in batch {event.batch_id} "
            f"is defective. Reason: {event.defect_reason}"
        ),
        severity=NotificationSeverity.WARNING,
        payload=payload,
    )
    return NotificationService.create_notification(
        db=db, notification_data=notification_data
    )


def handle_batch_completed(db: Session, payload: dict) -> NotificationResponse:

    event = BatchCompletedEvent.model_validate(payload)

    notification_data = NotificationCreate(
        event_type=event.event_type,
        title="Batch completed",
        message=(
            f"Batch {event.batch_number} completed. "
            f"Defect rate: {event.defect_rate}%"
        ),
        severity=NotificationSeverity.INFO,
        payload=payload,
    )
    return NotificationService.create_notification(
        db=db, notification_data=notification_data
    )


def handle_event(db: Session, payload: dict) -> NotificationResponse:

    event = BaseEvent.model_validate(payload)

    event_type = event.event_type

    if event_type == NotificationEventType.PART_DEFECTIVE_DETECTED:
        return handle_part_defective_detected(db, payload)

    if event_type == NotificationEventType.BATCH_COMPLETED:
        return handle_batch_completed(db, payload)

    raise ValueError(f"Unsupported event type: {event_type}")
