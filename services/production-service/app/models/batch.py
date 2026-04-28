from sqlalchemy import Integer, String, Float, DateTime, func, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from app.db.base import Base
from app.core.enums import BatchStatus



class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, 
        index=True, autoincrement=True
    )

    batch_number: Mapped[str] = mapped_column(
        String(100), unique=True,
        index=True, nullable=False
    )

    product_name: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )

    planned_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    produced_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)    
    accepted_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defect_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    length_target: Mapped[float] = mapped_column(Float, nullable=False)
    width_target: Mapped[float] = mapped_column(Float, nullable=False)
    height_target: Mapped[float] = mapped_column(Float, nullable=False)

    length_tolerance: Mapped[float] = mapped_column(Float, nullable=False)
    width_tolerance: Mapped[float] = mapped_column(Float, nullable=False)
    height_tolerance: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[BatchStatus] = mapped_column(SqlEnum(BatchStatus), nullable=False, default=BatchStatus.created, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )