from pydantic import BaseModel

from app.core.enums import NotificationEventType


class EventEnvelope(BaseModel):
    event_id: str
    event_type: NotificationEventType
    payload: dict


class PartDefectiveDetectedPayload(BaseModel):
    part_id: int
    batch_id: int
    defect_reason: str
    action: str | None = None
    timestamp: str | None = None


class BatchCompletedPayload(BaseModel):
    batch_number: str
    defect_rate: float
    timestamp: str | None = None
