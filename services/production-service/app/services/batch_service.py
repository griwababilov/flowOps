from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.batch_repository import BatchRepository
from app.schemas.batch import BatchCreate, BatchResponse, BatchUpdate, BatchStatsResponse
from app.core.enums import BatchStatus

from datetime import datetime, timezone


class BatchService:

    @staticmethod
    def create_batch(db: Session, batch_data: BatchCreate) -> BatchResponse:
        batch = BatchRepository.create(db=db, **batch_data.model_dump())

        return BatchResponse.model_validate(batch)

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )

        completion_rate = (
            batch.produced_quantity / batch.planned_quantity * 100
            if batch.planned_quantity > 0 else 0
        )

        defect_rate = (
            batch.defect_quantity / batch.produced_quantity * 100
            if batch.produced_quantity > 0 else 0
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
    def cancelled(db: Session, batch_id: int) -> BatchResponse:
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
    def delete(db: Session, batch_id: int) -> dict:
        deleted = BatchRepository.delete_by_id(db, batch_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found"
            )

        return {"message": "Batch deleted successfully"}
