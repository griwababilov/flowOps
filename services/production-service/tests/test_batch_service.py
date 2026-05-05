import pytest
from fastapi import HTTPException

from app.core.enums import BatchStatus
from app.repositories.batch_repository import BatchRepository
from app.schemas.batch import BatchCreate, BatchUpdate
from app.schemas.part import PartCreate
from app.services.batch_service import BatchService
from app.services.part_service import PartService


def make_batch_data(batch_number: str = "BATCH-SERVICE-001") -> BatchCreate:
    return BatchCreate(
        batch_number=batch_number,
        product_name="Test product",
        planned_quantity=10,
        length_target=100,
        width_target=50,
        height_target=20,
        length_tolerance=5,
        width_tolerance=2,
        height_tolerance=1,
    )


def create_test_batch(db_session, batch_number: str = "BATCH-SERVICE-001"):
    batch_response = BatchService.create_batch(
        db_session,
        make_batch_data(batch_number=batch_number),
    )

    return BatchRepository.get_by_id(db_session, batch_response.id)


def test_create_batch(db_session):
    batch = BatchService.create_batch(
        db_session,
        make_batch_data(),
    )

    assert batch.id is not None
    assert batch.batch_number == "BATCH-SERVICE-001"
    assert batch.product_name == "Test product"
    assert batch.planned_quantity == 10
    assert batch.produced_quantity == 0
    assert batch.status == BatchStatus.created


def test_get_batches(db_session):
    create_test_batch(db_session, "BATCH-001")
    create_test_batch(db_session, "BATCH-002")

    batches = BatchService.get_batches(db_session)

    batch_numbers = [batch.batch_number for batch in batches]

    assert len(batches) == 2
    assert "BATCH-001" in batch_numbers
    assert "BATCH-002" in batch_numbers


def test_get_batch_by_id(db_session):
    batch_model = create_test_batch(db_session, "BATCH-GET")

    batch = BatchService.get_batch_by_id(db_session, batch_model.id)

    assert batch.id == batch_model.id
    assert batch.batch_number == "BATCH-GET"


def test_get_batch_by_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.get_batch_by_id(db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"


def test_update_batch(db_session):
    batch_model = create_test_batch(db_session, "BATCH-UPDATE")

    updated_batch = BatchService.update_batch(
        db_session,
        batch_model.id,
        BatchUpdate(
            product_name="Updated product",
            planned_quantity=20,
            length_target=110,
            width_target=55,
            height_target=25,
            length_tolerance=6,
            width_tolerance=3,
            height_tolerance=2,
        ),
    )

    assert updated_batch.id == batch_model.id
    assert updated_batch.product_name == "Updated product"
    assert updated_batch.planned_quantity == 20


def test_update_batch_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.update_batch(
            db_session,
            999999,
            BatchUpdate(product_name="Updated product"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"


def test_update_batch_planned_quantity_less_than_produced_raises_400(db_session):
    batch_model = create_test_batch(db_session, "BATCH-PLANNED-CHECK")

    PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch_model.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch_model.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        BatchService.update_batch(
            db_session,
            batch_model.id,
            BatchUpdate(planned_quantity=1),
        )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "planned_quantity cannot be less than produced_quantity"
    )


def test_in_progress(db_session):
    batch_model = create_test_batch(db_session, "BATCH-IN-PROGRESS")

    batch = BatchService.in_progress(db_session, batch_model.id)

    assert batch.id == batch_model.id
    assert batch.status == BatchStatus.in_progress


def test_in_progress_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.in_progress(db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"


def test_cannot_move_to_in_progress_twice(db_session):
    batch_model = create_test_batch(db_session, "BATCH-IN-PROGRESS-TWICE")

    BatchService.in_progress(db_session, batch_model.id)

    with pytest.raises(HTTPException) as exc_info:
        BatchService.in_progress(db_session, batch_model.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Only created batches can be in_progress"


def test_complete(db_session):
    batch_model = create_test_batch(db_session, "BATCH-COMPLETE")

    BatchService.in_progress(db_session, batch_model.id)

    batch = BatchService.complete(db_session, batch_model.id)

    assert batch.id == batch_model.id
    assert batch.status == BatchStatus.completed
    assert batch.completed_at is not None


def test_complete_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.complete(db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"


def test_cannot_complete_created_batch(db_session):
    batch_model = create_test_batch(db_session, "BATCH-COMPLETE-INVALID")

    with pytest.raises(HTTPException) as exc_info:
        BatchService.complete(db_session, batch_model.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Only in_progress batches can be completed"


def test_cancel(db_session):
    batch_model = create_test_batch(db_session, "BATCH-CANCEL")

    batch = BatchService.cancel(db_session, batch_model.id)

    assert batch.id == batch_model.id
    assert batch.status == BatchStatus.cancelled


def test_cancel_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.cancel(db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"


def test_cannot_cancel_completed_batch(db_session):
    batch_model = create_test_batch(db_session, "BATCH-CANCEL-COMPLETED")

    BatchService.in_progress(db_session, batch_model.id)
    BatchService.complete(db_session, batch_model.id)

    with pytest.raises(HTTPException) as exc_info:
        BatchService.cancel(db_session, batch_model.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Completed batches can't be cancelled"


def test_get_stats_empty_batch(db_session):
    batch_model = create_test_batch(db_session, "BATCH-STATS-EMPTY")

    stats = BatchService.get_stats(db_session, batch_model.id)

    assert stats.batch_id == batch_model.id
    assert stats.planned_quantity == 10
    assert stats.produced_quantity == 0
    assert stats.good_quantity == 0
    assert stats.defective_quantity == 0
    assert stats.completion_rate == 0
    assert stats.defect_rate == 0


def test_get_stats_with_parts(db_session):
    batch_model = create_test_batch(db_session, "BATCH-STATS-WITH-PARTS")

    PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch_model.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch_model.id,
            length_actual=106,
            width_actual=50,
            height_actual=20,
        ),
    )

    stats = BatchService.get_stats(db_session, batch_model.id)

    assert stats.batch_id == batch_model.id
    assert stats.planned_quantity == 10
    assert stats.produced_quantity == 2
    assert stats.good_quantity == 1
    assert stats.defective_quantity == 1
    assert stats.completion_rate == 20
    assert stats.defect_rate == 50


def test_get_stats_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.get_stats(db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"


def test_delete_batch(db_session):
    batch_model = create_test_batch(db_session, "BATCH-DELETE")

    result = BatchService.delete_batch(db_session, batch_model.id)

    assert result == {"message": "Batch deleted successfully"}

    deleted_batch = BatchRepository.get_by_id(db_session, batch_model.id)

    assert deleted_batch is None


def test_delete_batch_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        BatchService.delete_batch(db_session, 999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"
