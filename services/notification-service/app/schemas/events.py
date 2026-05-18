from pydantic import BaseModel

from app.core.enums import NotificationEventType


class BaseEvent(BaseModel):
    event_type: NotificationEventType


class PartDefectiveDetectedEvent(BaseEvent):
    part_id: int
    batch_id: int
    defect_reason: str
    action: str | None = None
    timestamp: str | None = None


class BatchCompletedEvent(BaseEvent):
    batch_number: str
    defect_rate: float
    timestamp: str | None = None
