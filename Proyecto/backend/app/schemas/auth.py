from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


StaffRole = Literal[
    "ADMIN",
    "GUARD",
]


class LoginRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=80,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )

    @field_validator("username")
    @classmethod
    def normalize_username(
        cls,
        value: str,
    ) -> str:

        return (
            value
            .strip()
            .lower()
        )


class AuthUserResponse(BaseModel):

    id: int

    full_name: str

    username: str

    role: StaffRole

    active: bool


class LoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_in: int

    user: AuthUserResponse