from sqlalchemy.orm import Session

from app.models.batch import Batch


class BatchRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Batch:
        batch = Batch(**kwargs)
        db.add(batch)
        return batch

    @staticmethod
    def get_all(db: Session, limit=100, offset=0) -> list[Batch]:
        return (
            db.query(Batch)
            .order_by(Batch.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, batch_id: int) -> Batch | None:
        return db.query(Batch).filter(Batch.id == batch_id).first()

    @staticmethod
    def update(batch: Batch, **kwargs) -> Batch:
        for key, value in kwargs.items():
            setattr(batch, key, value)
        return batch

    @staticmethod
    def delete(db: Session, batch: Batch) -> None:
        db.delete(batch)
