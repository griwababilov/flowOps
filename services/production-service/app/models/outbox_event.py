from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, JSON, DateTime, func, Enum as SqlEnum, Text
from datetime import datetime

from app.core.enums import OutboxEventStatus
from app.db.base import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    event_type: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    routing_key: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    status: Mapped[OutboxEventStatus] = mapped_column(
        SqlEnum(OutboxEventStatus),
        nullable=False,
        index=True,
        default=OutboxEventStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
