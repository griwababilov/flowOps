from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.part_repository import PartRepository
from app.repositories.batch_repository import BatchRepository
from app.schemas.part import PartCreate, PartUpdate, PartResponse
from app.schemas.batch import BatchPartParametrs
from app.core.enums import DefectReason


class PartService:

    @staticmethod
    def create_part(db: Session, part_data: PartCreate) -> PartResponse:
        batch = BatchRepository.get_by_id(db, part_data.batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        if batch.accepted_quantity >= batch.planned_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Batch is already full"
            )

        is_defective, defect_reason = PartService.calculate_defect_status(
            batch, part_data
        )
        part = PartRepository.create(
            db=db,
            **part_data.model_dump(),
            is_defective=is_defective,
            defect_reason=defect_reason
        )

        batch.produced_quantity += 1

        if is_defective:
            batch.defect_quantity += 1
        else:
            batch.accepted_quantity += 1

        try:
            db.commit()
            db.refresh(part)
            db.refresh(batch)
            return PartResponse.model_validate(part)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_parts(db: Session) -> list[PartResponse]:
        parts = PartRepository.get_all(db)
        return list(map(PartResponse.model_validate, parts))

    @staticmethod
    def get_part_by_id(db: Session, part_id: int) -> PartResponse:
        part = PartRepository.get_by_id(db, part_id)

        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
            )

        return PartResponse.model_validate(part)

    @staticmethod
    def get_parts_in_batch(db: Session, batch_id: int) -> list[PartResponse]:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        parts = PartRepository.get_by_batch_id(db, batch_id)

        return list(map(PartResponse.model_validate, parts))

    @staticmethod
    def get_defective_parts_in_batch(db: Session, batch_id: int) -> list[PartResponse]:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        defective_parts = PartRepository.get_defective_parts_in_batch(db, batch_id)

        return list(map(PartResponse.model_validate, defective_parts))
    
    @staticmethod
    def _dimensions_changed(update_data: dict) -> bool:
        return any(
            field in update_data
            for field in ("length_actual", "width_actual", "height_actual")
        )


    @staticmethod
    def _manual_status_changed(update_data: dict) -> bool:
        return (
            "is_defective" in update_data
            or "defect_reason" in update_data
        )


    @staticmethod
    def _validate_manual_defect_logic(
        is_defective: bool,
        defect_reason: DefectReason | None,
        update_data: dict
    ) -> None:
        if is_defective is True and defect_reason is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="defect_reason is required when is_defective is True"
            )

        if is_defective is False:
            update_data["defect_reason"] = None

    @staticmethod
    def update_part(db: Session, part_id: int, part_data: PartUpdate) -> PartResponse:
        part = PartRepository.get_by_id(db, part_id)

        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        batch = BatchRepository.get_by_id(db, part.batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )

        old_is_defective = part.is_defective
        update_data = part_data.model_dump(exclude_unset=True)

        dimensions_changed = PartService._dimensions_changed(update_data)
        manual_status_changed = PartService._manual_status_changed(update_data)

        if dimensions_changed and not manual_status_changed:
            target_part_data = PartCreate(
                batch_id=part.batch_id,
                length_actual=update_data.get("length_actual", part.length_actual),
                width_actual=update_data.get("width_actual", part.width_actual),
                height_actual=update_data.get("height_actual", part.height_actual),
            )

            is_defective, defect_reason = PartService.calculate_defect_status(
                batch,
                target_part_data
            )

            update_data["is_defective"] = is_defective
            update_data["defect_reason"] = defect_reason

        else:
            target_is_defective = update_data.get("is_defective", part.is_defective)
            target_defect_reason = update_data.get("defect_reason", part.defect_reason)

            PartService._validate_manual_defect_logic(
                target_is_defective,
                target_defect_reason,
                update_data
            )

        try:
            updated_part = PartRepository.update(part, **update_data)

            if old_is_defective != updated_part.is_defective:
                if updated_part.is_defective:
                    batch.defect_quantity += 1
                    batch.accepted_quantity = max(batch.accepted_quantity - 1, 0)
                else:
                    batch.accepted_quantity += 1
                    batch.defect_quantity = max(batch.defect_quantity - 1, 0)

            db.commit()
            db.refresh(updated_part)
            db.refresh(batch)

            return PartResponse.model_validate(updated_part)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_part(db: Session, part_id: int) -> dict:
        part = PartRepository.get_by_id(db, part_id)

        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
            )

        batch = BatchRepository.get_by_id(db, part.batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        batch.produced_quantity = max(batch.produced_quantity - 1, 0)

        if part.is_defective:
            batch.defect_quantity = max(batch.defect_quantity - 1, 0)
        else:
            batch.accepted_quantity = max(batch.accepted_quantity - 1, 0)

        try:
            PartRepository.delete(db, part)
            db.commit()
            return {"message": "Part deleted successfully"}
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def calculate_defect_status(
        batch: BatchPartParametrs, part_data: PartCreate | PartUpdate
    ) -> tuple[bool, DefectReason | None]:

        min_length = batch.length_target - batch.length_tolerance
        max_length = batch.length_target + batch.length_tolerance

        min_width = batch.width_target - batch.width_tolerance
        max_width = batch.width_target + batch.width_tolerance

        min_height = batch.height_target - batch.height_tolerance
        max_height = batch.height_target + batch.height_tolerance

        if part_data.length_actual < min_length or part_data.length_actual > max_length:
            return (True, DefectReason.LENGTH_EXCEEDS_TOLERANCE)

        if part_data.width_actual < min_width or part_data.width_actual > max_width:
            return (True, DefectReason.WIDTH_EXCEEDS_TOLERANCE)

        if part_data.height_actual < min_height or part_data.height_actual > max_height:
            return (True, DefectReason.HEIGHT_EXCEEDS_TOLERANCE)

        return (False, None)
