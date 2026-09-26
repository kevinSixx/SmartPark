from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class PermissionDates(BaseModel):
    valid_from: datetime | None = None
    valid_to: datetime | None = None

    @field_validator("valid_from", "valid_to")
    @classmethod
    def normalize_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_period(self):
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must be greater than or equal to valid_from")
        return self


class PermissionCreate(PermissionDates):
    user_id: int
    vehicle_id: int
    active: bool = True


class PermissionUpdate(PermissionDates):
    active: bool | None = None

    @model_validator(mode="after")
    def reject_null_active(self):
        if "active" in self.model_fields_set and self.active is None:
            raise ValueError("active cannot be null")
        return self


class PermissionResponse(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    active: bool
    valid_from: datetime | None
    valid_to: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
