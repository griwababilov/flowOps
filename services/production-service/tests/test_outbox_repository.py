from uuid import uuid4

from app.core.enums import OutboxEventStatus
from app.models.outbox_event import OutboxEvent
from app.repositories.outbox_repository import OutboxRepository


def test_create_outbox_event(db_session):
    payload = {
        "event_type": "part.defective_detected",
        "part_id": 1,
        "batch_id": 1,
        "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
        "action": "created",
        "timestamp": "2026-05-21T10:00:00+00:00",
    }

    event = OutboxRepository.create(
        db=db_session,
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload=payload,
    )

    db_session.commit()
    db_session.refresh(event)

    assert event.id is not None
    assert event.event_type == "part.defective_detected"
    assert event.routing_key == "part.defective_detected"
    assert event.payload == payload
    assert event.status == OutboxEventStatus.PENDING
    assert event.published_at is None
    assert event.last_error is None


def test_claim_events_for_publish_returns_only_pending_available_events(db_session):
    pending_event = OutboxEvent(
        event_id=str(uuid4()),
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={
            "part_id": 1,
            "batch_id": 1,
            "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
        },
        status=OutboxEventStatus.PENDING,
    )

    failed_event = OutboxEvent(
        event_id=str(uuid4()),
        event_type="batch.completed",
        routing_key="batch.completed",
        payload={
            "batch_number": "BATCH-1",
            "defect_rate": 10.0,
        },
        status=OutboxEventStatus.FAILED,
        last_error="RabbitMQ is unavailable",
    )

    published_event = OutboxEvent(
        event_id=str(uuid4()),
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={
            "part_id": 2,
            "batch_id": 1,
            "defect_reason": "WIDTH_EXCEEDS_TOLERANCE",
        },
        status=OutboxEventStatus.PUBLISHED,
    )

    db_session.add_all([pending_event, failed_event, published_event])
    db_session.commit()

    events = OutboxRepository.claim_events_for_publish(db=db_session)

    event_ids = [event.id for event in events]

    assert pending_event.id in event_ids
    assert failed_event.id not in event_ids
    assert published_event.id not in event_ids

    assert pending_event.status == OutboxEventStatus.PROCESSING
    assert pending_event.locked_at is not None


def test_claim_events_for_publish_respects_limit(db_session):
    for index in range(3):
        event = OutboxEvent(
            event_id=str(uuid4()),
            event_type="part.defective_detected",
            routing_key="part.defective_detected",
            payload={
                "part_id": index + 1,
                "batch_id": 1,
                "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
                "action": "created",
            },
            status=OutboxEventStatus.PENDING,
        )
        db_session.add(event)

    db_session.commit()

    events = OutboxRepository.claim_events_for_publish(db=db_session, limit=2)

    assert len(events) == 2

    for event in events:
        assert event.status == OutboxEventStatus.PROCESSING
        assert event.locked_at is not None


def test_mark_as_published(db_session):
    event = OutboxEvent(
        event_id=str(uuid4()),
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={
            "part_id": 1,
            "batch_id": 1,
            "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
            "action": "created",
        },
        status=OutboxEventStatus.PROCESSING,
        last_error="Previous error",
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    OutboxRepository.mark_as_published(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.status == OutboxEventStatus.PUBLISHED
    assert event.published_at is not None
    assert event.last_error is None
    assert event.locked_at is None
    assert event.next_retry_at is None


def test_mark_for_retry(db_session):
    event = OutboxEvent(
        event_id=str(uuid4()),
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={
            "part_id": 1,
            "batch_id": 1,
            "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
            "action": "created",
        },
        status=OutboxEventStatus.PROCESSING,
        retry_count=0,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    OutboxRepository.mark_for_retry(
        outbox_event=event,
        error_message="RabbitMQ connection failed",
    )

    db_session.commit()
    db_session.refresh(event)

    assert event.status == OutboxEventStatus.PENDING
    assert event.last_error == "RabbitMQ connection failed"
    assert event.retry_count == 1
    assert event.locked_at is None
    assert event.next_retry_at is not None
