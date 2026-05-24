import json
import pika

from app.broker.rabbitmq import get_rabbitmq_channel, EXCHANGE_NAME


def publish_event(
    routing_key: str, event_id: str, event_type: str, payload: dict
) -> None:
    connection = None

    try:
        connection, channel = get_rabbitmq_channel()

        message_body = {
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload,
        }

        message = json.dumps(message_body, default=str)

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
