def test_create_notification(client):
    payload = {
        "event_id": "11111111-1111-1111-1111-111111111111",
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
    assert data["event_id"] == payload["event_id"]
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
        "event_id": "22222222-2222-2222-2222-222222222222",
        "event_type": "batch.completed",
        "title": "Batch completed",
        "message": "Batch 1 completed",
        "severity": "info",
        "payload": {"batch_number": "BATCH-001", "defect_rate": 0.0},
    }

    create_response = client.post("/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.get(f"/notifications/{notification_id}")

    assert response.status_code == 200
    assert response.json()["id"] == notification_id
    assert response.json()["event_id"] == payload["event_id"]


def test_get_notification_not_found(client):
    response = client.get("/notifications/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_mark_notification_as_read(client):
    payload = {
        "event_id": "33333333-3333-3333-3333-333333333333",
        "event_type": "part.defective_detected",
        "title": "Defective part detected",
        "message": "Part 2 is defective",
        "severity": "warning",
        "payload": {
            "part_id": 2,
            "batch_id": 1,
            "defect_reason": "WIDTH_EXCEEDS_TOLERANCE",
        },
    }

    create_response = client.post("/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.patch(f"/notifications/{notification_id}/read")

    assert response.status_code == 200
    assert response.json()["is_read"] is True
    assert response.json()["event_id"] == payload["event_id"]


def test_delete_notification(client):
    payload = {
        "event_id": "44444444-4444-4444-4444-444444444444",
        "event_type": "batch.completed",
        "title": "Batch completed",
        "message": "Batch 2 completed",
        "severity": "info",
        "payload": {"batch_number": "BATCH-002", "defect_rate": 5.0},
    }

    create_response = client.post("/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.delete(f"/notifications/{notification_id}")

    assert response.status_code == 204

    get_response = client.get(f"/notifications/{notification_id}")

    assert get_response.status_code == 404


def test_create_notification_is_idempotent_by_event_id(client):
    payload = {
        "event_id": "55555555-5555-5555-5555-555555555555",
        "event_type": "part.defective_detected",
        "title": "Defective part detected",
        "message": "Part 5 is defective",
        "severity": "warning",
        "payload": {
            "part_id": 5,
            "batch_id": 1,
            "defect_reason": "HEIGHT_EXCEEDS_TOLERANCE",
        },
    }

    first_response = client.post("/notifications/", json=payload)
    second_response = client.post("/notifications/", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code in (200, 201)

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["id"] == second_data["id"]
    assert first_data["event_id"] == second_data["event_id"]
