from pika import BlockingConnection, URLParameters
import os
from pika.adapters.blocking_connection import BlockingChannel

EXCHANGE_NAME: str = "flowops.events"


def get_rabbitmq_connection() -> BlockingConnection:
    connection = BlockingConnection(URLParameters(os.getenv["RABBITMQ_URL"]))

    return connection


def get_rabbitmq_channel() -> tuple[BlockingConnection, BlockingChannel]:
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
    )

    return connection, channel
