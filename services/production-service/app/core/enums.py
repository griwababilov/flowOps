from enum import Enum


class BatchStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"