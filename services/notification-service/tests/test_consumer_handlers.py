import pytest
from pydantic import ValidationError

from app.consumer.handlers import handle_batch_completed
from app.consumer.handlers import handle_event
from app.consumer.handlers import handle_part_defective_detected
from app.core.enums import NotificationEventType
from app.core.enums import NotificationSeverity
from app.models.notification import Notification


def test_handle_part_defective_detected_creates_notification(db_session):
    payload = {
        "event_type": "part.defective_detected",
        "part_id": 10,
        "batch_id": 3,
        "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
        "action": "created",
        "timestamp": "2026-05-15T12:00:00+00:00",
    }

    notification = handle_part_defective_detected(db_session, payload)

    assert notification.id > 0
    assert notification.event_type == NotificationEventType.PART_DEFECTIVE_DETECTED
    assert notification.title == "Defective part detected"
    assert notification.severity == NotificationSeverity.WARNING
    assert notification.payload == payload
    assert "Part 10 in batch 3 is defective" in notification.message

    db_notification = db_session.query(Notification).first()

    assert db_notification is not None
    assert db_notification.id == notification.id


def test_handle_batch_completed_creates_notification(db_session):
    payload = {
        "event_type": "batch.completed",
        "batch_id": 5,
        "batch_number": "BATCH-005",
        "product_name": "Test Product",
        "planned_quantity": 100,
        "produced_quantity": 100,
        "accepted_quantity": 95,
        "defect_quantity": 5,
        "defect_rate": 5.0,
        "timestamp": "2026-05-15T12:00:00+00:00",
    }

    notification = handle_batch_completed(db_session, payload)

    assert notification.id > 0
    assert notification.event_type == NotificationEventType.BATCH_COMPLETED
    assert notification.title == "Batch completed"
    assert notification.severity == NotificationSeverity.INFO
    assert notification.payload == payload
    assert "Batch BATCH-005 completed" in notification.message
    assert "Defect rate: 5.0%" in notification.message


def test_handle_event_dispatches_part_defective_detected(db_session):
    payload = {
        "event_type": "part.defective_detected",
        "part_id": 15,
        "batch_id": 7,
        "defect_reason": "WIDTH_EXCEEDS_TOLERANCE",
        "action": "updated",
        "timestamp": "2026-05-15T12:00:00+00:00",
    }

    notification = handle_event(db_session, payload)

    assert notification.event_type == NotificationEventType.PART_DEFECTIVE_DETECTED
    assert notification.severity == NotificationSeverity.WARNING


def test_handle_event_dispatches_batch_completed(db_session):
    payload = {
        "event_type": "batch.completed",
        "batch_id": 8,
        "batch_number": "BATCH-008",
        "defect_rate": 2.5,
    }

    notification = handle_event(db_session, payload)

    assert notification.event_type == NotificationEventType.BATCH_COMPLETED
    assert notification.severity == NotificationSeverity.INFO


def test_handle_event_unsupported_event_type_raises_error(db_session):
    payload = {
        "event_type": "unknown.event",
    }

    with pytest.raises(ValidationError):
        handle_event(db_session, payload)
