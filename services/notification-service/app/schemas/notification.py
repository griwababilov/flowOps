from pydantic import BaseModel, ConfigDict
from pydantic import Field

from app.core.enums import NotificationEventType, NotificationSeverity

from datetime import datetime


class NotificationCreate(BaseModel):
    event_type: NotificationEventType

    title: str = Field(max_length=255)
    message: str = Field(max_length=1023)

    severity: NotificationSeverity = Field(default=NotificationSeverity.INFO)
    payload: dict | None = None


class NotificationResponse(BaseModel):
    id: int = Field(ge=0)
    event_type: NotificationEventType

    title: str = Field(max_length=255)
    message: str = Field(max_length=1023)

    severity: NotificationSeverity
    is_read: bool
    payload: dict | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationReadUpdate(BaseModel):
    is_read: bool
