from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.part_repository import PartRepository
from app.repositories.batch_repository import BatchRepository
from app.schemas.part import PartCreate, PartUpdate, PartResponse


class PartService:

    @staticmethod
    def create_part(db: Session, part_data: PartCreate) -> PartResponse:
        batch = BatchRepository.get_by_id(db, part_data.batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        if batch.produced_quantity >= batch.planned_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Batch is already full"
            )

        part = PartRepository.create_without_commit(db=db, **part_data.model_dump())

        batch.produced_quantity += 1

        if part_data.is_defective:
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
    def patch_part(db: Session, part_id: int, part_data: PartUpdate) -> PartResponse:
        part = PartRepository.get_by_id(db, part_id)

        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
            )

        update_data = part_data.model_dump(exclude_unset=True)

        update_part = PartRepository.update(db, part, **update_data)

        return PartResponse.model_validate(update_part)

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
