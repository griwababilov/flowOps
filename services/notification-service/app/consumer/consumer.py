import json

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from app.consumer.handlers import handle_event
from app.consumer.rabbitmq import QUEUE_NAME, get_channel
from app.db.session import SessionLocal
from app.schemas.events import EventEnvelope
import logging

logger = logging.getLogger(__name__)


def process_message(
    channel: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
) -> None:
    db = SessionLocal()

    try:
        message = EventEnvelope.model_validate(json.loads(body.decode("utf-8")))

        handle_event(
            db=db,
            event_id=message.event_id,
            event_type=message.event_type,
            payload=message.payload,
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception:
        logger.exception("Failed to process RabbitMQ message")
        db.rollback()
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )

    finally:
        db.close()


def start_consumer() -> None:
    connection, channel = get_channel()

    try:
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=process_message,
            auto_ack=False,
        )

        print(f"Consumer started. Listening queue: {QUEUE_NAME}")
        channel.start_consuming()

    finally:
        if connection and connection.is_open:
            connection.close()


if __name__ == "__main__":
    start_consumer()
