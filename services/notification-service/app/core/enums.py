from enum import Enum


class NotificationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class NotificationEventType(str, Enum):
    PART_CREATED = "part.created"
    PART_UPDATED = "part.updated"
    PART_DELETED = "part.deleted"
    PART_DEFECTIVE_DETECTED = "part.defective_detected"

    BATCH_CREATED = "batch.created"
    BATCH_UPDATED = "batch.updated"
    BATCH_COMPLETED = "batch.completed"
    BATCH_CANCELLED = "batch.cancelled"
