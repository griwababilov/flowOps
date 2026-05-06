def test_create_notification(client):
    payload = {
        "event_type": "part.defective_detected",
        "title": "Defective part detected",
        "message": "Part 1 is defective",
        "severity": "warning",
        "payload": {
            "part_id": 1,
            "batch_id": 1,
            "defect_reason": "LENGTH_EXCEEDS_TOLERANCE",
        },
    }

    response = client.post("/notifications/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["event_type"] == payload["event_type"]
    assert data["title"] == payload["title"]
    assert data["message"] == payload["message"]
    assert data["severity"] == payload["severity"]
    assert data["is_read"] is False
    assert data["payload"] == payload["payload"]


def test_get_notifications(client):
    response = client.get("/notifications/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_notification_by_id(client):
    payload = {
        "event_type": "batch.completed",
        "title": "Batch completed",
        "message": "Batch 1 completed",
        "severity": "info",
        "payload": {"batch_id": 1},
    }

    create_response = client.post("/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.get(f"/notifications/{notification_id}")

    assert response.status_code == 200
    assert response.json()["id"] == notification_id


def test_get_notification_not_found(client):
    response = client.get("/notifications/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_mark_notification_as_read(client):
    payload = {
        "event_type": "part.defective_detected",
        "title": "Defective part detected",
        "message": "Part 2 is defective",
        "severity": "warning",
        "payload": {"part_id": 2},
    }

    create_response = client.post("/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.patch(f"/notifications/{notification_id}/read")

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_delete_notification(client):
    payload = {
        "event_type": "batch.completed",
        "title": "Batch completed",
        "message": "Batch 2 completed",
        "severity": "info",
        "payload": {"batch_id": 2},
    }

    create_response = client.post("/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.delete(f"/notifications/{notification_id}")

    assert response.status_code == 204

    get_response = client.get(f"/notifications/{notification_id}")

    assert get_response.status_code == 404
