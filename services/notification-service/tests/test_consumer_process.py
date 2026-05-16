import json
from unittest.mock import Mock
from unittest.mock import patch

from app.consumer.consumer import process_message


def test_process_message_ack_on_success():
    channel = Mock()
    method = Mock()
    method.delivery_tag = 1
    properties = Mock()

    payload = {
        "event_type": "part.defective_detected",
        "part_id": 1,
        "batch_id": 1,
        "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
    }

    body = json.dumps(payload).encode("utf-8")

    with patch("app.consumer.consumer.SessionLocal") as mock_session_local:
        db = Mock()
        mock_session_local.return_value = db

        with patch("app.consumer.consumer.handle_event") as mock_handle_event:
            process_message(channel, method, properties, body)

    mock_handle_event.assert_called_once_with(db=db, payload=payload)
    channel.basic_ack.assert_called_once_with(delivery_tag=1)
    channel.basic_nack.assert_not_called()
    db.close.assert_called_once()


def test_process_message_nack_on_error():
    channel = Mock()
    method = Mock()
    method.delivery_tag = 2
    properties = Mock()

    payload = {
        "event_type": "unknown.event",
    }

    body = json.dumps(payload).encode("utf-8")

    with patch("app.consumer.consumer.SessionLocal") as mock_session_local:
        db = Mock()
        mock_session_local.return_value = db

        with patch("app.consumer.consumer.handle_event") as mock_handle_event:
            mock_handle_event.side_effect = ValueError("Unsupported event type")

            try:
                process_message(channel, method, properties, body)
            except ValueError:
                pass

    mock_handle_event.assert_called_once_with(db=db, payload=payload)
    db.rollback.assert_called_once()
    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_called_once_with(
        delivery_tag=2,
        requeue=False,
    )
    db.close.assert_called_once()
