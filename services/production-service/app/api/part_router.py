from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.part import PartCreate, PartResponse, PartUpdate
from app.services.part_service import PartService

router = APIRouter(prefix="/production", tags=["Parts"])


@router.post("/parts", response_model=PartResponse, status_code=201)
def create_part(part_data: PartCreate, db=Depends(get_db)):
    return PartService.create_part(db, part_data)


@router.get("/parts", response_model=list[PartResponse])
def get_parts(db=Depends(get_db)):
    return PartService.get_parts(db)


@router.get("/parts/{part_id}", response_model=PartResponse)
def get_part(part_id: int, db=Depends(get_db)):
    return PartService.get_part_by_id(db, part_id)


@router.patch("/parts/{part_id}", response_model=PartResponse)
def update_part(part_id: int, part_data: PartUpdate, db=Depends(get_db)):
    return PartService.update_part(db, part_id, part_data)


@router.delete("/parts/{part_id}")
def delete_part(part_id: int, db=Depends(get_db)):
    return PartService.delete_part(db, part_id)


@router.get("/batches/{batch_id}/parts", response_model=list[PartResponse])
def get_parts_in_batch(batch_id: int, db=Depends(get_db)):
    return PartService.get_parts_in_batch(db, batch_id)


@router.get("/batches/{batch_id}/parts/defective", response_model=list[PartResponse])
def get_defective_parts_in_batch(batch_id: int, db=Depends(get_db)):
    return PartService.get_defective_parts_in_batch(db, batch_id)
