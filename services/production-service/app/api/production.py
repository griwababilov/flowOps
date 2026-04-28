from fastapi import APIRouter, Depends
from app.schemas.batch import (
    BatchCreate,
    BatchResponse,
)

router = APIRouter(prefix="/production", tags=["Production"])

@router.post("/batches", response_model=BatchResponse, status_code=201)
def create_batch():
    pass


@router.get("/batches")
def get_batches():
    pass


@router.get("/batches/{batch_id}")
def get_batch(batch_id: int):
    pass


@router.patch("/batches/{batch_id}")
def patch_batch(batch_id: int):
    pass


@router.post("/batches/{batch_id}/complete")
def complete_batch(batch_id: int):
    pass


@router.delete("/batches/{batch_id}")
def delete_batch(batch_id: int):
    pass