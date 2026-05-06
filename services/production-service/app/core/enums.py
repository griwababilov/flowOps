from enum import Enum


class BatchStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DefectReason(str, Enum):
    LENGTH_EXCEEDS_TOLERANCE = (
        "length_exceeds_tolerance"  # Длина превышает допустимое отклонение
    )
    WIDTH_EXCEEDS_TOLERANCE = (
        "width_exceeds_tolerance"  # Ширина превышает допустимое отклонение
    )
    HEIGHT_EXCEEDS_TOLERANCE = (
        "height_exceeds_tolerance"  # Высота превышает допустимое отклонение
    )

    SURFACE_DAMAGE = "SURFACE_DAMAGE"  # Повреждение поверхности
    GEOMETRY_DISTORTION = "GEOMETRY_DISTORTION"  # Геометрическая деформация

    SENSOR_ERROR = "SENSOR_ERROR"  # Ошибка датчика / измерения
    MANUAL_REJECTION = "MANUAL_REJECTION"  # Ручная отбраковка оператором
