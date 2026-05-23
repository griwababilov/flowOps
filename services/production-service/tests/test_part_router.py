from app.core.enums import OutboxEventStatus
from app.models.outbox_event import OutboxEvent


def make_batch_payload(batch_number="Batch-for-parts"):
    return {
        "batch_number": batch_number,
        "product_name": "Name-test",
        "planned_quantity": 10,
        "length_target": 100,
        "width_target": 50,
        "height_target": 20,
        "length_tolerance": 5,
        "width_tolerance": 2,
        "height_tolerance": 1,
    }


def create_batch(client, batch_number="Batch-for-parts"):
    response = client.post(
        "/production/batches",
        json=make_batch_payload(batch_number=batch_number),
    )

    assert response.status_code == 201

    return response.json()


def make_part_payload(batch_id: int, length=100, width=50, height=20):
    return {
        "batch_id": batch_id,
        "length_actual": length,
        "width_actual": width,
        "height_actual": height,
    }


def create_part(client, batch_id: int, length=100, width=50, height=20):
    response = client.post(
        "/production/parts",
        json=make_part_payload(
            batch_id=batch_id,
            length=length,
            width=width,
            height=height,
        ),
    )

    assert response.status_code == 201

    return response.json()


def test_create_accepted_part(client):
    batch = create_batch(client)

    response = client.post(
        "/production/parts",
        json=make_part_payload(batch["id"]),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["batch_id"] == batch["id"]
    assert data["is_defective"] is False
    assert data["defect_reason"] is None


def test_create_defective_part_by_length(client):
    batch = create_batch(client)

    response = client.post(
        "/production/parts",
        json=make_part_payload(batch["id"], length=106),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["is_defective"] is True
    assert data["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"


def test_get_parts(client):
    batch = create_batch(client)

    create_part(client, batch["id"])
    create_part(client, batch["id"], length=106)

    response = client.get("/production/parts")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2


def test_get_part_by_id(client):
    batch = create_batch(client)
    part = create_part(client, batch["id"])

    response = client.get(f"/production/parts/{part['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == part["id"]
    assert data["batch_id"] == batch["id"]


def test_get_part_not_found(client):
    response = client.get("/production/parts/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Part not found"


def test_get_parts_in_batch(client):
    batch = create_batch(client)

    create_part(client, batch["id"])
    create_part(client, batch["id"], length=106)

    response = client.get(f"/production/batches/{batch['id']}/parts")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(part["batch_id"] == batch["id"] for part in data)


def test_get_defective_parts_in_batch(client):
    batch = create_batch(client)

    create_part(client, batch["id"])
    create_part(client, batch["id"], length=106)

    response = client.get(f"/production/batches/{batch['id']}/parts/defective")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["is_defective"] is True
    assert data[0]["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"


def test_patch_part_dimensions_recalculates_defect(client):
    batch = create_batch(client)
    part = create_part(client, batch["id"])

    response = client.patch(
        f"/production/parts/{part['id']}",
        json={"length_actual": 106},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_defective"] is True
    assert data["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"


def test_patch_part_manual_rejection(client):
    batch = create_batch(client)
    part = create_part(client, batch["id"])

    response = client.patch(
        f"/production/parts/{part['id']}",
        json={
            "is_defective": True,
            "defect_reason": "MANUAL_REJECTION",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_defective"] is True
    assert data["defect_reason"] == "MANUAL_REJECTION"


def test_patch_part_remove_defect(client):
    batch = create_batch(client)
    part = create_part(client, batch["id"], length=106)

    response = client.patch(
        f"/production/parts/{part['id']}",
        json={"is_defective": False},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_defective"] is False
    assert data["defect_reason"] is None


def test_patch_part_not_found(client):
    response = client.patch(
        "/production/parts/999999",
        json={"length_actual": 100},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Part not found"


def test_delete_part(client):
    batch = create_batch(client)
    part = create_part(client, batch["id"])

    response = client.delete(f"/production/parts/{part['id']}")

    assert response.status_code == 200
    assert response.json() == {"message": "Part deleted successfully"}

    get_response = client.get(f"/production/parts/{part['id']}")

    assert get_response.status_code == 404


def test_delete_part_not_found(client):
    response = client.delete("/production/parts/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Part not found"


def test_create_part_with_invalid_batch_returns_404(client):
    response = client.post(
        "/production/parts",
        json=make_part_payload(batch_id=999999),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Batch not found"


def test_create_part_with_invalid_dimensions_returns_422(client):
    batch = create_batch(client)

    response = client.post(
        "/production/parts",
        json=make_part_payload(batch["id"], length=0),
    )

    assert response.status_code == 422


def test_create_defective_part_creates_outbox_event(client, db_session):
    batch = create_batch(client, batch_number="Outbox-defective-create")

    response = client.post(
        "/production/parts",
        json=make_part_payload(batch["id"], length=106),
    )

    assert response.status_code == 201

    part = response.json()

    assert part["is_defective"] is True
    assert part["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"

    outbox_event = (
        db_session.query(OutboxEvent)
        .filter(OutboxEvent.event_type == "part.defective_detected")
        .order_by(OutboxEvent.id.desc())
        .first()
    )

    assert outbox_event is not None
    assert outbox_event.routing_key == "part.defective_detected"
    assert outbox_event.status == OutboxEventStatus.PENDING

    assert outbox_event.payload["event_type"] == "part.defective_detected"
    assert outbox_event.payload["part_id"] == part["id"]
    assert outbox_event.payload["batch_id"] == batch["id"]
    assert outbox_event.payload["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"
    assert outbox_event.payload["action"] == "created"
    assert outbox_event.payload["timestamp"] is not None


def test_create_accepted_part_does_not_create_outbox_event(client, db_session):
    batch = create_batch(client, batch_number="Outbox-accepted-create")

    before_count = db_session.query(OutboxEvent).count()

    response = client.post(
        "/production/parts",
        json=make_part_payload(batch["id"]),
    )

    assert response.status_code == 201

    part = response.json()

    assert part["is_defective"] is False
    assert part["defect_reason"] is None

    after_count = db_session.query(OutboxEvent).count()

    assert after_count == before_count


def test_patch_accepted_part_to_defective_creates_outbox_event(client, db_session):
    batch = create_batch(client, batch_number="Outbox-defective-update")
    part = create_part(client, batch["id"])

    assert part["is_defective"] is False

    response = client.patch(
        f"/production/parts/{part['id']}",
        json={"length_actual": 106},
    )

    assert response.status_code == 200

    updated_part = response.json()

    assert updated_part["is_defective"] is True
    assert updated_part["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"

    outbox_event = (
        db_session.query(OutboxEvent)
        .filter(OutboxEvent.event_type == "part.defective_detected")
        .order_by(OutboxEvent.id.desc())
        .first()
    )

    assert outbox_event is not None
    assert outbox_event.routing_key == "part.defective_detected"
    assert outbox_event.status == OutboxEventStatus.PENDING

    assert outbox_event.payload["event_type"] == "part.defective_detected"
    assert outbox_event.payload["part_id"] == part["id"]
    assert outbox_event.payload["batch_id"] == batch["id"]
    assert outbox_event.payload["defect_reason"] == "LENGTH_EXCEEDS_TOLERANCE"
    assert outbox_event.payload["action"] == "update"
    assert outbox_event.payload["timestamp"] is not None


def test_patch_defective_part_to_defective_does_not_create_duplicate_outbox_event(
    client,
    db_session,
):
    batch = create_batch(client, batch_number="Outbox-no-duplicate-update")
    part = create_part(client, batch["id"], length=106)

    assert part["is_defective"] is True

    before_count = (
        db_session.query(OutboxEvent)
        .filter(OutboxEvent.event_type == "part.defective_detected")
        .count()
    )

    response = client.patch(
        f"/production/parts/{part['id']}",
        json={"width_actual": 53},
    )

    assert response.status_code == 200

    updated_part = response.json()

    assert updated_part["is_defective"] is True

    after_count = (
        db_session.query(OutboxEvent)
        .filter(OutboxEvent.event_type == "part.defective_detected")
        .count()
    )

    assert after_count == before_count


def test_create_last_part_creates_batch_completed_outbox_event(client, db_session):
    batch_payload = make_batch_payload(batch_number="Outbox-batch-completed")
    batch_payload["planned_quantity"] = 1

    batch_response = client.post("/production/batches", json=batch_payload)

    assert batch_response.status_code == 201

    batch = batch_response.json()
    batch_id = batch["id"]

    in_progress_response = client.post(f"/production/batches/{batch_id}/in-progress")

    assert in_progress_response.status_code == 200

    response = client.post(
        "/production/parts",
        json=make_part_payload(batch_id),
    )

    assert response.status_code == 201

    outbox_event = (
        db_session.query(OutboxEvent)
        .filter(OutboxEvent.event_type == "batch.completed")
        .order_by(OutboxEvent.id.desc())
        .first()
    )

    assert outbox_event is not None
    assert outbox_event.routing_key == "batch.completed"
    assert outbox_event.status == OutboxEventStatus.PENDING

    assert outbox_event.payload["event_type"] == "batch.completed"
    assert outbox_event.payload["batch_number"] == "Outbox-batch-completed"
    assert outbox_event.payload["defect_rate"] == 0.0
    assert outbox_event.payload["timestamp"] is not None
