from pydantic import BaseModel, ConfigDict

from app.core.enums import NotificationEventType, NotificationSeverity

from datetime import datetime


class NotificationCreate(BaseModel):
    event_id: str
    event_type: NotificationEventType
    title: str
    message: str
    severity: NotificationSeverity = NotificationSeverity.INFO
    payload: dict | None = None


class NotificationResponse(BaseModel):
    id: int
    event_id: str
    event_type: NotificationEventType
    title: str
    message: str
    severity: NotificationSeverity
    is_read: bool
    payload: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationReadUpdate(BaseModel):
    is_read: bool
