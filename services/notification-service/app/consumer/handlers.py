from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.core.enums import NotificationEventType, NotificationSeverity
from app.schemas.events import (
    PartDefectiveDetectedPayload,
    BatchCompletedPayload,
)


def handle_part_defective_detected(
    db: Session,
    event_id: str,
    event_type: str,
    payload: dict,
) -> NotificationResponse:

    event = PartDefectiveDetectedPayload.model_validate(payload)

    notification_data = NotificationCreate(
        event_id=event_id,
        event_type=event_type,
        title="Defective part detected",
        message=(
            f"Part {event.part_id} in batch {event.batch_id} "
            f"is defective. Reason: {event.defect_reason}"
        ),
        severity=NotificationSeverity.WARNING,
        payload=payload,
    )

    return NotificationService.create_notification(
        db=db,
        notification_data=notification_data,
    )


def handle_batch_completed(
    db: Session,
    event_id: str,
    event_type: str,
    payload: dict,
) -> NotificationResponse:

    event = BatchCompletedPayload.model_validate(payload)

    notification_data = NotificationCreate(
        event_id=event_id,
        event_type=event_type,
        title="Batch completed",
        message=(
            f"Batch {event.batch_number} completed. "
            f"Defect rate: {event.defect_rate}%"
        ),
        severity=NotificationSeverity.INFO,
        payload=payload,
    )

    return NotificationService.create_notification(
        db=db,
        notification_data=notification_data,
    )


def handle_event(
    db: Session,
    event_id: str,
    event_type: str,
    payload: dict,
) -> NotificationResponse | None:

    if event_type == NotificationEventType.PART_DEFECTIVE_DETECTED:
        return handle_part_defective_detected(
            db=db,
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )

    if event_type == NotificationEventType.BATCH_COMPLETED:
        return handle_batch_completed(
            db=db,
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )

    raise ValueError(f"Unsupported event type: {event_type}")
