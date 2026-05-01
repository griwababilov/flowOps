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


def test_create_batch(client):
    payload = make_batch_payload()

    response = client.post("/production/batches/", json=payload)

    assert response.status_code in [200, 201]

    data = response.json()

    assert data["batch_number"] == payload["batch_number"]
    assert data["product_name"] == payload["product_name"]
    assert data["planned_quantity"] == payload["planned_quantity"]

    assert "id" in data
    assert "status" in data
    assert "created_at" in data


def test_get_batches_list(client):
    payload_1 = make_batch_payload(batch_number="Batch-test-1")
    payload_2 = make_batch_payload(batch_number="Batch-test-2")

    client.post("/production/batches/", json=payload_1)
    client.post("/production/batches/", json=payload_2)

    response = client.get("/production/batches/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    batch_numbers = [batch["batch_number"] for batch in data]

    assert "Batch-test-1" in batch_numbers
    assert "Batch-test-2" in batch_numbers


def test_get_batch_by_id(client):
    payload = make_batch_payload(batch_number="Batch-get-by-id")

    create_response = client.post("/production/batches/", json=payload)
    created_batch = create_response.json()

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


def test_create_batch_with_zero_planned_quantity_returns_422(client):
    payload = make_batch_payload()
    payload["planned_quantity"] = 0

    response = client.post("/production/batches/", json=payload)

    assert response.status_code == 422


def test_create_batch_with_zero_length_target_returns_422(client):
    payload = make_batch_payload()
    payload["length_target"] = 0

    response = client.post("/production/batches/", json=payload)

    assert response.status_code == 422
