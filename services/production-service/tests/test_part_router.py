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
    assert data["defect_reason"] == "length_exceeds_tolerance"


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
    assert data[0]["defect_reason"] == "length_exceeds_tolerance"


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
    assert data["defect_reason"] == "length_exceeds_tolerance"


def test_patch_part_manual_rejection(client):
    batch = create_batch(client)
    part = create_part(client, batch["id"])

    response = client.patch(
        f"/production/parts/{part['id']}",
        json={
            "is_defective": True,
            "defect_reason": "manual_rejection",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_defective"] is True
    assert data["defect_reason"] == "manual_rejection"


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
