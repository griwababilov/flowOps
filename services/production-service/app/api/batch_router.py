from fastapi import APIRouter, Depends
from app.schemas.batch import BatchCreate, BatchResponse, BatchUpdate
from app.db.session import get_db
from app.services.batch_service import BatchService

router = APIRouter(prefix="/production", tags=["Production"])


@router.post("/batches", response_model=BatchResponse, status_code=201)
def create_batch(batch_data: BatchCreate, db=Depends(get_db)):
    return BatchService.create_batch(db, batch_data)


@router.get("/batches", response_model=list[BatchResponse])
def get_batches(db=Depends(get_db)):
    return BatchService.get_batches(db)


@router.get("/batches/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db=Depends(get_db)):
    return BatchService.get_batch_by_id(db, batch_id)


@router.patch("/batches/{batch_id}", response_model=BatchResponse)
def patch_batch(batch_id: int, batch_data: BatchUpdate, db = Depends(get_db)):
    return BatchService.patch_batch(db, batch_id, batch_data)


@router.post("/batches/{batch_id}/in-progress", response_model=BatchResponse)
def in_progress_batch(batch_id: int, db=Depends(get_db)):
    return BatchService.in_progress(db, batch_id)


@router.post("/batches/{batch_id}/complete", response_model=BatchResponse)
def complete_batch(batch_id: int, db = Depends(get_db)):
    return BatchService.compelete(db, batch_id)

@router.post("/batches/{batch_id}/cancelled", response_model=BatchResponse)
def cancelled_batch(batch_id: int, db = Depends(get_db)):
    return BatchService.compelete(db, batch_id)


@router.delete("/batches/{batch_id}")
def delete_batch(batch_id: int, db=Depends(get_db)):
    return BatchService.delete_batch(db, batch_id)

def delete_batch(batch_id: int, db=Depends(get_db)):
    return BatchService.delete(db, batch_id)
