from enum import Enum


class BatchStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


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

    SURFACE_DAMAGE = "surface_damage"  # Повреждение поверхности
    GEOMETRY_DISTORTION = "geometry_distortion"  # Геометрическая деформация

    SENSOR_ERROR = "sensor_error"  # Ошибка датчика / измерения
    MANUAL_REJECTION = "manual_rejection"  # Ручная отбраковка оператором
