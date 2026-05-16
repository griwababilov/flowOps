import logging
import os
import time

from pika import BlockingConnection, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError


log = logging.getLogger(__name__)

EXCHANGE_NAME: str = "flowops.events"
QUEUE_NAME: str = "notification-service.queue"

ROUTING_KEYS: tuple[str, ...] = (
    "batch.completed",
    "part.defective_detected",
)


def get_connection() -> BlockingConnection:
    rabbitmq_url = os.getenv("RABBITMQ_URL")

    if rabbitmq_url is None:
        raise RuntimeError("RABBITMQ_URL is not set")

    parameters = URLParameters(rabbitmq_url)

    while True:
        try:
            connection = BlockingConnection(parameters)
            log.info("Connected to RabbitMQ")
            return connection

        except AMQPConnectionError:
            log.warning("RabbitMQ is not ready yet. Retrying in 3 seconds...")
            time.sleep(3)


def get_channel() -> tuple[BlockingConnection, BlockingChannel]:
    connection = get_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="topic",
        durable=True,
    )

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    for routing_key in ROUTING_KEYS:
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=routing_key,
        )

    return connection, channel