from enum import Enum


class BatchStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DefectReason(str, Enum):
    LENGTH_EXCEEDS_TOLERANCE = (
        "LENGTH_EXCEEDS_TOLERANCE"  # Длина превышает допустимое отклонение
    )
    WIDTH_EXCEEDS_TOLERANCE = (
        "WIDTH_EXCEEDS_TOLERANCE"  # Ширина превышает допустимое отклонение
    )
    HEIGHT_EXCEEDS_TOLERANCE = (
        "HEIGHT_EXCEEDS_TOLERANCE"  # Высота превышает допустимое отклонение
    )

    SURFACE_DAMAGE = "SURFACE_DAMAGE"  # Повреждение поверхности
    GEOMETRY_DISTORTION = "GEOMETRY_DISTORTION"  # Геометрическая деформация

    SENSOR_ERROR = "SENSOR_ERROR"  # Ошибка датчика / измерения
    MANUAL_REJECTION = "MANUAL_REJECTION"  # Ручная отбраковка оператором


class OutboxEventStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
