from datetime import datetime

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator, model_validator


Name = Annotated[str, StringConstraints(min_length=1, max_length=120)]
InstitutionalId = Annotated[str, StringConstraints(min_length=1, max_length=50)]
Status = Literal["ACTIVE", "INACTIVE"]


class UserCreate(BaseModel):
    name: Name
    institutional_id: InstitutionalId

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("name cannot be empty")
        return value

    @field_validator("institutional_id")
    @classmethod
    def normalize_institutional_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().upper()
        if not value:
            raise ValueError("institutional_id cannot be empty")
        return value


class UserUpdate(BaseModel):
    name: Name | None = None
    institutional_id: InstitutionalId | None = None
    status: Status | None = None

    _normalize_name = field_validator("name")(UserCreate.normalize_name.__func__)
    _normalize_institutional_id = field_validator("institutional_id")(
        UserCreate.normalize_institutional_id.__func__
    )

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field in ("name", "institutional_id", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class UserResponse(BaseModel):
    id: int
    name: str
    institutional_id: str
    status: Status
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
