import pytest
from fastapi import HTTPException

from app.core.enums import DefectReason
from app.repositories.batch_repository import BatchRepository
from app.services.part_service import PartService
from app.schemas.part import PartCreate, PartUpdate


def create_test_batch(db, planned_quantity: int = 10):
    batch = BatchRepository.create(
        db=db,
        batch_number="B-001",
        product_name="Test product",
        planned_quantity=planned_quantity,
        length_target=100,
        width_target=50,
        height_target=20,
        length_tolerance=5,
        width_tolerance=2,
        height_tolerance=1,
    )

    db.commit()
    db.refresh(batch)

    return batch


def test_create_accepted_part(db_session):
    batch = create_test_batch(db_session)

    part_data = PartCreate(
        batch_id=batch.id,
        length_actual=100,
        width_actual=50,
        height_actual=20,
    )

    part = PartService.create_part(db_session, part_data)

    db_session.refresh(batch)

    assert part.is_defective is False
    assert part.defect_reason is None

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 1
    assert batch.defect_quantity == 0


def test_create_defective_part_by_length(db_session):
    batch = create_test_batch(db_session)

    part_data = PartCreate(
        batch_id=batch.id,
        length_actual=106,
        width_actual=50,
        height_actual=20,
    )

    part = PartService.create_part(db_session, part_data)

    db_session.refresh(batch)

    assert part.is_defective is True
    assert part.defect_reason == DefectReason.LENGTH_EXCEEDS_TOLERANCE

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 1


def test_create_defective_part_by_width(db_session):
    batch = create_test_batch(db_session)

    part_data = PartCreate(
        batch_id=batch.id,
        length_actual=100,
        width_actual=53,
        height_actual=20,
    )

    part = PartService.create_part(db_session, part_data)

    db_session.refresh(batch)

    assert part.is_defective is True
    assert part.defect_reason == DefectReason.WIDTH_EXCEEDS_TOLERANCE

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 1


def test_create_defective_part_by_height(db_session):
    batch = create_test_batch(db_session)

    part_data = PartCreate(
        batch_id=batch.id,
        length_actual=100,
        width_actual=50,
        height_actual=22,
    )

    part = PartService.create_part(db_session, part_data)

    db_session.refresh(batch)

    assert part.is_defective is True
    assert part.defect_reason == DefectReason.HEIGHT_EXCEEDS_TOLERANCE

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 1


def test_update_part_dimensions_recalculates_defect_status(db_session):
    batch = create_test_batch(db_session)

    part = PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    updated_part = PartService.update_part(
        db_session,
        part.id,
        PartUpdate(length_actual=106),
    )

    db_session.refresh(batch)

    assert updated_part.is_defective is True
    assert updated_part.defect_reason == DefectReason.LENGTH_EXCEEDS_TOLERANCE

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 1


def test_update_part_manual_rejection(db_session):
    batch = create_test_batch(db_session)

    part = PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    updated_part = PartService.update_part(
        db_session,
        part.id,
        PartUpdate(
            is_defective=True,
            defect_reason=DefectReason.MANUAL_REJECTION,
        ),
    )

    db_session.refresh(batch)

    assert updated_part.is_defective is True
    assert updated_part.defect_reason == DefectReason.MANUAL_REJECTION

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 1


def test_update_part_remove_defect_status(db_session):
    batch = create_test_batch(db_session)

    part = PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch.id,
            length_actual=106,
            width_actual=50,
            height_actual=20,
        ),
    )

    updated_part = PartService.update_part(
        db_session,
        part.id,
        PartUpdate(is_defective=False),
    )

    db_session.refresh(batch)

    assert updated_part.is_defective is False
    assert updated_part.defect_reason is None

    assert batch.produced_quantity == 1
    assert batch.accepted_quantity == 1
    assert batch.defect_quantity == 0


def test_delete_accepted_part_updates_batch_counters(db_session):
    batch = create_test_batch(db_session)

    part = PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    result = PartService.delete_part(db_session, part.id)

    db_session.refresh(batch)

    assert result == {"message": "Part deleted successfully"}

    assert batch.produced_quantity == 0
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 0


def test_delete_defective_part_updates_batch_counters(db_session):
    batch = create_test_batch(db_session)

    part = PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch.id,
            length_actual=106,
            width_actual=50,
            height_actual=20,
        ),
    )

    result = PartService.delete_part(db_session, part.id)

    db_session.refresh(batch)

    assert result == {"message": "Part deleted successfully"}

    assert batch.produced_quantity == 0
    assert batch.accepted_quantity == 0
    assert batch.defect_quantity == 0


def test_cannot_create_part_when_accepted_quantity_reaches_planned_quantity(db_session):
    batch = create_test_batch(db_session, planned_quantity=1)

    PartService.create_part(
        db_session,
        PartCreate(
            batch_id=batch.id,
            length_actual=100,
            width_actual=50,
            height_actual=20,
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        PartService.create_part(
            db_session,
            PartCreate(
                batch_id=batch.id,
                length_actual=100,
                width_actual=50,
                height_actual=20,
            ),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Batch is already full"


def test_create_part_with_non_existing_batch_raises_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        PartService.create_part(
            db_session,
            PartCreate(
                batch_id=999,
                length_actual=100,
                width_actual=50,
                height_actual=20,
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Batch not found"