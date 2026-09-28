from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


GateActionType = Literal[
    "OPEN",
    "CLOSE",
]

GateActionSource = Literal[
    "AUTO",
    "MANUAL",
]

GateActionStatus = Literal[
    "SUCCESS",
    "ERROR",
]


class ManualGateActionRequest(BaseModel):

    access_event_id: int | None = Field(
        default=None,
        ge=1
    )

    reason: str | None = Field(
        default=None,
        max_length=255
    )

    observation: str | None = Field(
        default=None,
        max_length=500
    )


class GateActionCreate(BaseModel):

    gate_id: str = Field(
        default="gate-01",
        min_length=1,
        max_length=50
    )

    action: GateActionType

    source: GateActionSource

    staff_id: int | None = Field(
        default=None,
        ge=1
    )

    access_event_id: int | None = Field(
        default=None,
        ge=1
    )

    reason: str | None = Field(
        default=None,
        max_length=255
    )

    observation: str | None = Field(
        default=None,
        max_length=500
    )

    status: GateActionStatus = "SUCCESS"

    error_message: str | None = Field(
        default=None,
        max_length=500
    )


class GateActionResponse(BaseModel):

    id: int

    timestamp: datetime

    gate_id: str

    action: GateActionType

    source: GateActionSource

    staff_id: int | None

    access_event_id: int | None

    reason: str | None

    observation: str | None

    status: GateActionStatus

    error_message: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )