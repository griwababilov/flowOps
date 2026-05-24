import time

from app.broker.publisher import publish_event
from app.repositories.outbox_repository import OutboxRepository
from app.db.session import SessionLocal

PUBLISH_INTERVAL_SECONDS = 5


def process_outbox_events() -> None:
    db = SessionLocal()

    try:

        events_for_publish = OutboxRepository.claim_events_for_publish(db=db)
        db.commit()

        for event in events_for_publish:
            try:
                publish_event(
                    routing_key=event.routing_key,
                    event_id=event.event_id,
                    event_type=event.event_type,
                    payload=event.payload,
                )
                OutboxRepository.mark_as_published(event)

            except Exception as exc:
                OutboxRepository.mark_for_retry(
                    outbox_event=event, error_message=str(exc)
                )

            db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def main() -> None:
    while True:
        process_outbox_events()
        time.sleep(PUBLISH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
