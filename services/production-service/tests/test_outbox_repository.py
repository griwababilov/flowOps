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
    assert event.error_message is None


def test_get_events_for_publish_returns_pending_and_failed(db_session):
    pending_event = OutboxEvent(
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={"event_type": "part.defective_detected"},
        status=OutboxEventStatus.PENDING,
    )

    failed_event = OutboxEvent(
        event_type="batch.completed",
        routing_key="batch.completed",
        payload={"event_type": "batch.completed"},
        status=OutboxEventStatus.FAILED,
        error_message="RabbitMQ is unavailable",
    )

    published_event = OutboxEvent(
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={"event_type": "part.defective_detected"},
        status=OutboxEventStatus.PUBLISHED,
    )

    db_session.add_all([pending_event, failed_event, published_event])
    db_session.commit()

    events = OutboxRepository.get_events_for_publish(db=db_session)

    event_ids = [event.id for event in events]

    assert pending_event.id in event_ids
    assert failed_event.id in event_ids
    assert published_event.id not in event_ids


def test_get_events_for_publish_respects_limit(db_session):
    for index in range(3):
        event = OutboxEvent(
            event_type="part.defective_detected",
            routing_key="part.defective_detected",
            payload={
                "event_type": "part.defective_detected",
                "index": index,
            },
            status=OutboxEventStatus.PENDING,
        )
        db_session.add(event)

    db_session.commit()

    events = OutboxRepository.get_events_for_publish(db=db_session, limit=2)

    assert len(events) == 2


def test_mark_as_published(db_session):
    event = OutboxEvent(
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={"event_type": "part.defective_detected"},
        status=OutboxEventStatus.FAILED,
        error_message="Previous error",
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    OutboxRepository.mark_as_published(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.status == OutboxEventStatus.PUBLISHED
    assert event.published_at is not None
    assert event.error_message is None


def test_mark_as_failed(db_session):
    event = OutboxEvent(
        event_type="part.defective_detected",
        routing_key="part.defective_detected",
        payload={"event_type": "part.defective_detected"},
        status=OutboxEventStatus.PENDING,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    OutboxRepository.mark_as_failed(
        outbox_event=event,
        error_message="RabbitMQ connection failed",
    )

    db_session.commit()
    db_session.refresh(event)

    assert event.status == OutboxEventStatus.FAILED
    assert event.error_message == "RabbitMQ connection failed"
