from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.core.enums import NotificationEventType, NotificationSeverity


def handle_part_defective_detected(db: Session, payload: dict) -> NotificationResponse:
    notification_data = NotificationCreate(
        event_type=NotificationEventType.PART_DEFECTIVE_DETECTED,
        title="Defective part detected",
        message=(
            f"Part {payload['part_id']} in batch {payload['batch_id']} "
            f"is defective. Reason: {payload['defect_reason']}"
        ),
        severity=NotificationSeverity.WARNING,
        payload=payload,
    )
    return NotificationService.create_notification(
        db=db, notification_data=notification_data
    )


def handle_batch_completed(db: Session, payload: dict) -> NotificationResponse:
    notification_data = NotificationCreate(
        event_type=NotificationEventType.BATCH_COMPLETED,
        title="Batch completed",
        message=(
            f"Batch {payload['batch_number']} completed. "
            f"Defect rate: {payload['defect_rate']}%"
        ),
        severity=NotificationSeverity.INFO,
        payload=payload,
    )
    return NotificationService.create_notification(
        db=db, notification_data=notification_data
    )


def handle_event(db: Session, payload: dict) -> NotificationResponse:
    event_type = payload["event_type"]

    if event_type == NotificationEventType.PART_DEFECTIVE_DETECTED.value:
        return handle_part_defective_detected(db, payload)

    if event_type == NotificationEventType.BATCH_COMPLETED.value:
        return handle_batch_completed(db, payload)

    raise ValueError(f"Unsupported event type: {event_type}")
