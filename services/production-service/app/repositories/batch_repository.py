from sqlalchemy.orm import Session

from app.models.batch import Batch


class BatchRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Batch:
        batch = Batch(**kwargs)
        try:
            db.add(batch)
            db.commit()
            db.refresh(batch)
            return batch
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_all(db: Session, limmit=100, offset=0) -> list[Batch]:
        return (db.query(Batch)
                .order_by(Batch.created_at.desc())
                .offset(offset)
                .limit(limmit)
                .all())

    @staticmethod
    def get_by_id(db: Session, batch_id: int) -> Batch | None:
        return db.query(Batch).filter(Batch.id == batch_id).first()
    
    @staticmethod
    def update(db: Session, batch: Batch, **kwargs) -> Batch:
        try:
            for key, value in kwargs.items():
                setattr(batch, key, value)

            db.commit()
            db.refresh(batch)

            return batch

        except Exception:
            db.rollback()
            raise
    
    @staticmethod
    def delete(db: Session, batch: Batch):
        try:
            db.delete(batch)
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_by_id(db: Session, batch_id: int) -> bool:
        try:
            deleted_rows = db.query(Batch).filter(Batch.id == batch_id).delete()
            db.commit()
            return deleted_rows > 0
        except Exception:
            db.rollback()
            raise