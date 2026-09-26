from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator, model_validator


Plate = Annotated[str, StringConstraints(min_length=1, max_length=20)]
OptionalText = Annotated[str, StringConstraints(min_length=1, max_length=60)]
VehicleStatus = Literal["ACTIVE", "INACTIVE"]


def normalize_plate(value: str | None) -> str | None:
    if value is None:
        return None
    value = "".join(value.split()).upper()
    if not value:
        raise ValueError("plate cannot be empty")
    return value


class VehicleCreate(BaseModel):
    user_id: int
    plate: Plate
    brand: OptionalText | None = None
    model: OptionalText | None = None
    color: Annotated[str, StringConstraints(min_length=1, max_length=40)] | None = None
    status: VehicleStatus = "ACTIVE"

    _normalize_plate = field_validator("plate")(normalize_plate)

    @field_validator("brand", "model", "color")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class VehicleUpdate(BaseModel):
    user_id: int | None = None
    plate: Plate | None = None
    brand: OptionalText | None = None
    model: OptionalText | None = None
    color: Annotated[str, StringConstraints(min_length=1, max_length=40)] | None = None
    status: VehicleStatus | None = None

    _normalize_plate = field_validator("plate")(normalize_plate)
    _strip_optional_text = field_validator("brand", "model", "color")(
        VehicleCreate.strip_optional_text.__func__
    )

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field in ("user_id", "plate", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class VehicleResponse(BaseModel):
    id: int
    user_id: int
    plate: str
    brand: str | None
    model: str | None
    color: str | None
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
