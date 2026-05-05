from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Boolean,
    Float,
    DateTime,
    func,
    Enum as SqlEnum,
)

from datetime import datetime
from typing import TYPE_CHECKING

from app.db.base import Base
from app.core.enums import DefectReason

if TYPE_CHECKING:
    from app.models.batch import Batch


class Part(Base):
    __tablename__ = "parts"

    __table_args__ = (
        # Фактические размеры должны быть больше нуля
        CheckConstraint("length_actual > 0", name="check_length_actual_positive"),
        CheckConstraint("width_actual > 0", name="check_width_actual_positive"),
        CheckConstraint("height_actual > 0", name="check_height_actual_positive"),
        # Если деталь НЕ бракована → причина брака должна отсутствовать
        CheckConstraint(
            "(is_defective = FALSE AND defect_reason IS NULL) OR "
            "(is_defective = TRUE)",
            name="check_defect_reason_consistency",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("batches.id", ondelete="CASCADE"), index=True, nullable=False
    )

    length_actual: Mapped[float] = mapped_column(Float, nullable=False)
    width_actual: Mapped[float] = mapped_column(Float, nullable=False)
    height_actual: Mapped[float] = mapped_column(Float, nullable=False)

    is_defective: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    defect_reason: Mapped[DefectReason | None] = mapped_column(
        SqlEnum(DefectReason), nullable=True, index=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    batch: Mapped["Batch"] = relationship(
        "Batch",
        back_populates="parts",
    )
