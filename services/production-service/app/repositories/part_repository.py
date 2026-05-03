from sqlalchemy.orm import Session

from app.models.part import Part


class PartRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Part:
        part = Part(**kwargs)

        try:
            db.add(part)
            db.commit()
            db.refresh(part)
            return part
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_all(db: Session) -> list[Part]:
        return db.query(Part).all()

    @staticmethod
    def get_by_id(db: Session, part_id: int) -> Part:
        return db.query(Part).filter(Part.id == part_id).first()

    @staticmethod
    def get_by_batch_id(db: Session, batch_id) -> list[Part]:
        return db.query(Part).filter(Part.batch_id == batch_id).all()

    @staticmethod
    def update(db: Session, part: Part, **kwargs) -> Part:
        try:
            for key, value in kwargs.items():
                setattr(part, key, value)

            db.commit()
            db.refresh(part)

            return part

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_by_id(db: Session, part_id: int) -> bool:
        try:
            deleted_rows = db.query(Part).filter(Part.id == part_id).delete()
            db.commit()
            return deleted_rows > 0
        except Exception:
            db.rollback()
            raise
