from pydantic import BaseModel, ConfigDict, Field, model_validator

from datetime import datetime

from app.core.enums import DefectReason


class PartCreate(BaseModel):
    batch_id: int = Field(ge=0)

    length_actual: float = Field(gt=0)
    width_actual: float = Field(gt=0)
    height_actual: float = Field(gt=0)


class PartPatch(BaseModel):
    batch_id: int | None = Field(default=None, ge=0)

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
