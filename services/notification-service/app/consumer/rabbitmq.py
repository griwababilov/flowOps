from pika import BlockingConnection, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
import os

EXCHANGE_NAME: str = "flowops.events"
QUEUE_NAME: str = "notification-service.queue"
ROUTING_KEYS: tuple[str, ...] = (
    "batch.completed",
    "part.defective_detected",
)


def get_connection() -> BlockingConnection:
    connection = BlockingConnection(URLParameters(os.getenv("RABBITMQ_URL")))

    return connection


def get_channel() -> tuple[BlockingConnection, BlockingChannel]:
    connection = get_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
    )
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    for routing_key in ROUTING_KEYS:
        channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=routing_key
        )

    return connection, channel
