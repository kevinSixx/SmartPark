from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


StaffRole = Literal["ADMIN", "GUARD"]


class StaffAccountCreate(BaseModel):
    full_name: str = Field(
        min_length=3,
        max_length=150
    )

    username: str = Field(
        min_length=3,
        max_length=80
    )

    password: str = Field(
        min_length=6,
        max_length=128
    )

    role: StaffRole

    active: bool = True

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(
        cls,
        value: str
    ) -> str:
        return " ".join(
            value.strip().split()
        )

    @field_validator("username")
    @classmethod
    def normalize_username(
        cls,
        value: str
    ) -> str:
        return (
            value
            .strip()
            .lower()
        )


class StaffAccountUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=150
    )

    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=128
    )

    role: StaffRole | None = None

    active: bool | None = None

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        return " ".join(
            value.strip().split()
        )


class StaffAccountResponse(BaseModel):
    id: int

    full_name: str

    username: str

    role: StaffRole

    active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )