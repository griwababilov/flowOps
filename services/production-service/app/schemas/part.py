from pydantic import BaseModel, ConfigDict, Field, model_validator

from datetime import datetime

from app.core.enums import DefectReason


class PartCreate(BaseModel):
    batch_id: int = Field(gt=0)

    length_actual: float = Field(gt=0)
    width_actual: float = Field(gt=0)
    height_actual: float = Field(gt=0)

    is_defective: bool = False
    defect_reason: DefectReason | None = None

    @model_validator(mode="after")
    def validate_defect_logic(self):
        if self.is_defective and self.defect_reason is None:
            raise ValueError("defect_reason is required when is_defective is True")

        if not self.is_defective and self.defect_reason is not None:
            raise ValueError("defect_reason must be null when is_defective is False")

        return self


class PartUpdate(BaseModel):
    is_defective: bool | None = None
    defect_reason: DefectReason | None = None

    length_actual: float | None = Field(default=None, gt=0)
    width_actual: float | None = Field(default=None, gt=0)
    height_actual: float | None = Field(default=None, gt=0)


class PartResponse(BaseModel):
    id: int
    batch_id: int

    length_actual: float
    width_actual: float
    height_actual: float

    is_defective: bool
    defect_reason: DefectReason | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
