from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    JSON,
    DateTime,
    func,
    Enum as SqlEnum,
)

from app.db.base import Base
from app.core.enums import NotificationEventType, NotificationSeverity

from datetime import datetime


class Notification(Base):

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    event_type: Mapped[NotificationEventType] = mapped_column(
        SqlEnum(NotificationEventType), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    severity: Mapped[NotificationSeverity] = mapped_column(
        SqlEnum(NotificationSeverity),
        default=NotificationSeverity.INFO,
        index=True,
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
