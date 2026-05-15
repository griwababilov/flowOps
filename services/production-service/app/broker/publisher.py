import json
import pika

from app.broker.rabbitmq import get_rabbitmq_channel, EXCHANGE_NAME


def publish_event(routing_key: str, payload: dict) -> None:
    connection = None

    try:
        connection, channel = get_rabbitmq_channel()
        message = json.dumps(payload, default=str)

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json",
            ),
        )
    finally:
        if connection and connection.is_open:
            connection.close()
