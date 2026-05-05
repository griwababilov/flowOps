from sqlalchemy.orm import Session

from app.models.part import Part


class PartRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Part:
        part = Part(**kwargs)
        db.add(part)
        return part

    @staticmethod
    def get_all(db: Session) -> list[Part]:
        return db.query(Part).all()

    @staticmethod
    def get_by_id(db: Session, part_id: int) -> Part:
        return db.query(Part).filter(Part.id == part_id).first()

    @staticmethod
    def get_by_batch_id(db: Session, batch_id: int) -> list[Part]:
        return db.query(Part).filter(Part.batch_id == batch_id).all()

    @staticmethod
    def get_defective_parts_in_batch(db: Session, batch_id: int) -> list[Part]:
        return db.query(Part).filter(Part.batch_id == batch_id, Part.is_defective).all()

    @staticmethod
    def update(part: Part, **kwargs) -> Part:
        for key, value in kwargs.items():
            setattr(part, key, value)

        return part

    @staticmethod
    def delete(db: Session, part: Part) -> None:
        db.delete(part)
