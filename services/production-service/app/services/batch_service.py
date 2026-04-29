from sqlalchemy.orm import Session

from app.schemas.batch import BatchCreate, BatchResponse


class BatchService:

    @staticmethod
    def create_batch(
        db: Session, batch_number: int, product_name: str,
        batch_data: BatchCreate
    ) -> BatchResponse:
        pass
    
        
