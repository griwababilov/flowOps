def make_batch_payload(batch_number="Batch-test"):
    return {
        "batch_number": batch_number,
        "product_name": "Name-test",
        "planned_quantity": 50000,
        "length_target": 1,
        "width_target": 1,
        "height_target": 1,
        "length_tolerance": 0,
        "width_tolerance": 0,
        "height_tolerance": 0,
    }


def create_batch(client, batch_number="Batch-test"):
    payload = make_batch_payload(batch_number=batch_number)
    response = client.post("/production/batches", json=payload)

    assert response.status_code == 201

    return response.json(), payload


def test_create_batch(client):
    created_batch, payload = create_batch(client)

    assert created_batch["batch_number"] == payload["batch_number"]
    assert created_batch["product_name"] == payload["product_name"]
    assert created_batch["planned_quantity"] == payload["planned_quantity"]

    assert "id" in created_batch
    assert "status" in created_batch
    assert "created_at" in created_batch


def test_get_batches_list(client):
    create_batch(client, batch_number="Batch-test-1")
    create_batch(client, batch_number="Batch-test-2")

    response = client.get("/production/batches")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    batch_numbers = [batch["batch_number"] for batch in data]

    assert "Batch-test-1" in batch_numbers
    assert "Batch-test-2" in batch_numbers


def test_get_batch_by_id(client):
    created_batch, payload = create_batch(client, batch_number="Batch-get-by-id")

    batch_id = created_batch["id"]

    response = client.get(f"/production/batches/{batch_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == batch_id
    assert data["batch_number"] == payload["batch_number"]
    assert data["product_name"] == payload["product_name"]
    assert data["planned_quantity"] == payload["planned_quantity"]


def test_get_batch_not_found(client):
    response = client.get("/production/batches/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Batch not found"


def test_create_batch_with_zero_planned_quantity_returns_422(client):
    payload = make_batch_payload()
    payload["planned_quantity"] = 0

    response = client.post("/production/batches", json=payload)

    assert response.status_code == 422


def test_create_batch_with_zero_length_target_returns_422(client):
    payload = make_batch_payload()
    payload["length_target"] = 0

    response = client.post("/production/batches", json=payload)

    assert response.status_code == 422


def test_update_batch(client):
    created_batch, _ = create_batch(client, batch_number="Batch-update")

    batch_id = created_batch["id"]

    payload = {
        "product_name": "Updated product",
        "planned_quantity": 100,
        "length_target": 10,
        "width_target": 5,
        "height_target": 2,
        "length_tolerance": 1,
        "width_tolerance": 0.5,
        "height_tolerance": 0.2,
    }

    response = client.patch(f"/production/batches/{batch_id}", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == batch_id
    assert data["product_name"] == "Updated product"
    assert data["planned_quantity"] == 100


def test_update_batch_not_found(client):
    response = client.patch(
        "/production/batches/999999",
        json={"product_name": "Updated product"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Batch not found"


def test_update_batch_planned_quantity_less_than_produced_returns_400(client):
    created_batch, _ = create_batch(
        client,
        batch_number="Batch-planned-quantity-check",
    )

    batch_id = created_batch["id"]

    part_payload = {
        "batch_id": batch_id,
        "length_actual": 1,
        "width_actual": 1,
        "height_actual": 1,
    }

    part_response = client.post("/production/parts", json=part_payload)
    assert part_response.status_code == 201

    response = client.patch(
        f"/production/batches/{batch_id}",
        json={"planned_quantity": 0},
    )

    assert response.status_code == 422


def test_update_batch_planned_quantity_less_than_produced_after_valid_schema_returns_400(
    client,
):
    created_batch, _ = create_batch(
        client,
        batch_number="Batch-planned-less-produced",
    )

    batch_id = created_batch["id"]

    part_payload = {
        "batch_id": batch_id,
        "length_actual": 1,
        "width_actual": 1,
        "height_actual": 1,
    }

    part_response_1 = client.post("/production/parts", json=part_payload)
    part_response_2 = client.post("/production/parts", json=part_payload)

    assert part_response_1.status_code == 201
    assert part_response_2.status_code == 201

    response = client.patch(
        f"/production/batches/{batch_id}",
        json={"planned_quantity": 1},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "planned_quantity cannot be less than produced_quantity"
    )


def test_move_batch_to_in_progress(client):
    created_batch, _ = create_batch(client, batch_number="Batch-in-progress")

    batch_id = created_batch["id"]

    response = client.post(f"/production/batches/{batch_id}/in-progress")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == batch_id
    assert data["status"] == "in_progress"


def test_cannot_move_batch_to_in_progress_twice(client):
    created_batch, _ = create_batch(client, batch_number="Batch-in-progress-twice")

    batch_id = created_batch["id"]

    first_response = client.post(f"/production/batches/{batch_id}/in-progress")
    second_response = client.post(f"/production/batches/{batch_id}/in-progress")

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Only created batches can be in_progress"


def test_complete_batch(client):
    created_batch, _ = create_batch(client, batch_number="Batch-complete")

    batch_id = created_batch["id"]

    in_progress_response = client.post(f"/production/batches/{batch_id}/in-progress")
    assert in_progress_response.status_code == 200

    response = client.post(f"/production/batches/{batch_id}/complete")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == batch_id
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_cannot_complete_created_batch(client):
    created_batch, _ = create_batch(client, batch_number="Batch-complete-invalid")

    batch_id = created_batch["id"]

    response = client.post(f"/production/batches/{batch_id}/complete")

    assert response.status_code == 400
    assert response.json()["detail"] == "Only in_progress batches can be completed"


def test_cancel_batch(client):
    created_batch, _ = create_batch(client, batch_number="Batch-cancel")

    batch_id = created_batch["id"]

    response = client.post(f"/production/batches/{batch_id}/cancel")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == batch_id
    assert data["status"] == "cancelled"


def test_cannot_cancel_completed_batch(client):
    created_batch, _ = create_batch(client, batch_number="Batch-cancel-completed")

    batch_id = created_batch["id"]

    in_progress_response = client.post(f"/production/batches/{batch_id}/in-progress")
    complete_response = client.post(f"/production/batches/{batch_id}/complete")

    assert in_progress_response.status_code == 200
    assert complete_response.status_code == 200

    response = client.post(f"/production/batches/{batch_id}/cancel")

    assert response.status_code == 400
    assert response.json()["detail"] == "Completed batches can't be cancelled"


def test_delete_batch(client):
    created_batch, _ = create_batch(client, batch_number="Batch-delete")

    batch_id = created_batch["id"]

    response = client.delete(f"/production/batches/{batch_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Batch deleted successfully"}

    get_response = client.get(f"/production/batches/{batch_id}")

    assert get_response.status_code == 404


def test_delete_batch_not_found(client):
    response = client.delete("/production/batches/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Batch not found"
