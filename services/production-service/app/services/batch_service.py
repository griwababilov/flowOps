from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.batch_repository import BatchRepository
from app.models.batch import Batch
from app.schemas.batch import BatchCreate, BatchResponse, BatchUpdate
from app.core.enums import BatchStatus

from datetime import datetime, timezone


class BatchService:

    @staticmethod
    def create_batch(db: Session, batch_data: BatchCreate) -> Batch:
        batch = BatchRepository.create(db=db, **batch_data.model_dump())

        return BatchResponse.model_validate(batch)

    @staticmethod
    def get_batches(db: Session) -> list[Batch]:
        batches = BatchRepository.get_all(db)
        return list(map(BatchResponse.model_validate, batches))

    @staticmethod
    def get_batch_by_id(db: Session, batch_id: int) -> Batch | None:
        batch = BatchRepository.get_by_id(db, batch_id)
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        return BatchResponse.model_validate(batch)

    @staticmethod
    def patch_batch(
        db: Session, batch_id: int, batch_data: BatchUpdate
    ) -> BatchResponse:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        update_data = batch_data.model_dump(exclude_unset=True)

        updated_batch = BatchRepository.update(db=db, batch=batch, **update_data)

        return BatchResponse.model_validate(updated_batch)

    @staticmethod
    def in_progress(db: Session, batch_id) -> BatchRepository:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        if batch.status != BatchStatus.created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only created batches can be in_progress",
            )

        comleted_batch = BatchRepository.update(
            db,
            batch,
            status=BatchStatus.in_progress,
        )

        return BatchResponse.model_validate(comleted_batch)

    @staticmethod
    def compelete(db: Session, batch_id) -> BatchResponse:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        if batch.status != BatchStatus.in_progress:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only in_progress batches can be completed",
            )

        comleted_batch = BatchRepository.update(
            db,
            batch,
            status=BatchStatus.completed,
            completed_at=datetime.now(timezone.utc),
        )

        return BatchResponse.model_validate(comleted_batch)

    @staticmethod
    def cancelled(db: Session, batch_id: int):
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        if batch.status == BatchStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed batches can't be cancelled",
            )

        comleted_batch = BatchRepository.update(
            db,
            batch,
            status=BatchStatus.cancelled,
        )

        return BatchResponse.model_validate(comleted_batch)

    @staticmethod
    def delete(db: Session, batch_id: int) -> bool:
        deleted = BatchRepository.delete_by_id(db, batch_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        return {"message": "Batch deleted successfully"}
