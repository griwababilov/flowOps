import json
from unittest.mock import Mock
from unittest.mock import patch

from app.consumer.consumer import process_message


def test_process_message_ack_on_success():
    channel = Mock()
    method = Mock()
    method.delivery_tag = 1
    properties = Mock()

    message = {
        "event_id": "11111111-1111-1111-1111-111111111111",
        "event_type": "part.defective_detected",
        "payload": {
            "part_id": 1,
            "batch_id": 1,
            "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
            "action": "created",
        },
    }

    body = json.dumps(message).encode("utf-8")

    with patch("app.consumer.consumer.SessionLocal") as mock_session_local:
        db = Mock()
        mock_session_local.return_value = db

        with patch("app.consumer.consumer.handle_event") as mock_handle_event:
            process_message(channel, method, properties, body)

    mock_handle_event.assert_called_once_with(
        db=db,
        event_id=message["event_id"],
        event_type=message["event_type"],
        payload=message["payload"],
    )
    channel.basic_ack.assert_called_once_with(delivery_tag=1)
    channel.basic_nack.assert_not_called()
    db.rollback.assert_not_called()
    db.close.assert_called_once()


def test_process_message_nack_on_unknown_event_type():
    channel = Mock()
    method = Mock()
    method.delivery_tag = 2
    properties = Mock()

    message = {
        "event_id": "22222222-2222-2222-2222-222222222222",
        "event_type": "unknown.event",
        "payload": {},
    }

    body = json.dumps(message).encode("utf-8")

    with patch("app.consumer.consumer.SessionLocal") as mock_session_local:
        db = Mock()
        mock_session_local.return_value = db

        with patch("app.consumer.consumer.handle_event") as mock_handle_event:
            process_message(channel, method, properties, body)

    mock_handle_event.assert_not_called()
    db.rollback.assert_called_once()
    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_called_once_with(
        delivery_tag=2,
        requeue=False,
    )
    db.close.assert_called_once()


def test_process_message_nack_on_invalid_json():
    channel = Mock()
    method = Mock()
    method.delivery_tag = 3
    properties = Mock()

    body = b"{invalid-json"

    with patch("app.consumer.consumer.SessionLocal") as mock_session_local:
        db = Mock()
        mock_session_local.return_value = db

        with patch("app.consumer.consumer.handle_event") as mock_handle_event:
            process_message(channel, method, properties, body)

    mock_handle_event.assert_not_called()
    db.rollback.assert_called_once()
    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_called_once_with(
        delivery_tag=3,
        requeue=False,
    )
    db.close.assert_called_once()
