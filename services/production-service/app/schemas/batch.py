from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime

from app.core.enums import BatchStatus


class BatchCreate(BaseModel):
    batch_number: str
    product_name: str
    planned_quantity: int = Field(gt=0)

    length_target: float = Field(gt=0)
    width_target: float = Field(gt=0)
    height_target: float = Field(gt=0)

    length_tolerance: float = Field(ge=0)
    width_tolerance: float = Field(ge=0)
    height_tolerance: float = Field(ge=0)


class BatchResponse(BaseModel):
    id: int
    batch_number: str
    product_name: str
    planned_quantity: int
    status: BatchStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class BatchUpdate(BaseModel):
    product_name: str | None = None
    planned_quantity: int | None = Field(default=None, gt=0)

    length_target: float | None = Field(default=None, gt=0)
    width_target: float | None = Field(default=None, gt=0)
    height_target: float | None = Field(default=None, gt=0)

    length_tolerance: float | None = Field(default=None, ge=0)
    width_tolerance: float | None = Field(default=None, ge=0)
    height_tolerance: float | None = Field(default=None, ge=0)
