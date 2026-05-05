from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.batch_repository import BatchRepository
from app.schemas.batch import (
    BatchCreate,
    BatchResponse,
    BatchUpdate,
    BatchStatsResponse,
)
from app.core.enums import BatchStatus

from datetime import datetime, timezone


class BatchService:

    @staticmethod
    def create_batch(db: Session, batch_data: BatchCreate) -> BatchResponse:
        batch = BatchRepository.create(db=db, **batch_data.model_dump())
        try:
            db.commit()
            db.refresh(batch)
            return BatchResponse.model_validate(batch)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_batches(db: Session) -> list[BatchResponse]:
        batches = BatchRepository.get_all(db)
        return list(map(BatchResponse.model_validate, batches))

    @staticmethod
    def get_batch_by_id(db: Session, batch_id: int) -> BatchResponse | None:
        batch = BatchRepository.get_by_id(db, batch_id)
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        return BatchResponse.model_validate(batch)

    @staticmethod
    def get_stats(db: Session, batch_id: int) -> BatchStatsResponse:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        completion_rate = (
            batch.produced_quantity / batch.planned_quantity * 100
            if batch.planned_quantity > 0
            else 0
        )

        defect_rate = (
            batch.defect_quantity / batch.produced_quantity * 100
            if batch.produced_quantity > 0
            else 0
        )

        return BatchStatsResponse(
            batch_id=batch.id,
            planned_quantity=batch.planned_quantity,
            produced_quantity=batch.produced_quantity,
            good_quantity=batch.accepted_quantity,
            defective_quantity=batch.defect_quantity,
            completion_rate=completion_rate,
            defect_rate=defect_rate,
        )

    @staticmethod
    def update_batch(
        db: Session, batch_id: int, batch_data: BatchUpdate
    ) -> BatchResponse:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        update_data = batch_data.model_dump(exclude_unset=True)

        if "planned_quantity" in update_data:
            if update_data["planned_quantity"] < batch.produced_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="planned_quantity cannot be less than produced_quantity",
                )

        try:
            updated_batch = BatchRepository.update(batch=batch, **update_data)
            db.commit()
            db.refresh(updated_batch)

            return BatchResponse.model_validate(updated_batch)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def in_progress(db: Session, batch_id: int) -> BatchResponse:
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

        try:
            in_progress_batch = BatchRepository.update(
                batch,
                status=BatchStatus.in_progress,
            )

            db.commit()
            db.refresh(in_progress_batch)

            return BatchResponse.model_validate(in_progress_batch)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def complete(db: Session, batch_id: int) -> BatchResponse:
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

        try:
            completed_batch = BatchRepository.update(
                batch,
                status=BatchStatus.completed,
                completed_at=datetime.now(timezone.utc),
            )

            db.commit()
            db.refresh(completed_batch)

            return BatchResponse.model_validate(completed_batch)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def cancel(db: Session, batch_id: int) -> BatchResponse:
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

        try:
            cancelled_batch = BatchRepository.update(
                batch,
                status=BatchStatus.cancelled,
            )

            db.commit()
            db.refresh(cancelled_batch)

            return BatchResponse.model_validate(cancelled_batch)

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_batch(db: Session, batch_id: int) -> dict:
        batch = BatchRepository.get_by_id(db, batch_id)

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        try:
            BatchRepository.delete(db, batch)
            db.commit()
            return {"message": "Batch deleted successfully"}
        except Exception:
            db.rollback()
            raise
