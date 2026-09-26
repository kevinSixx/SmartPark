from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.schemas.vehicle import normalize_plate


EventType = Literal["ENTRY", "EXIT"]
Decision = Literal["AUTHORIZED", "REJECTED", "REVIEW"]


class AccessEventCreate(BaseModel):
    timestamp: datetime | None = None
    event_type: EventType
    user_id: int | None = None
    vehicle_id: int | None = None
    detected_plate: str | None = None
    face_score: float | None = Field(default=None, ge=0, le=1)
    plate_score: float | None = Field(default=None, ge=0, le=1)
    decision: Decision
    reason: str | None = Field(default=None, max_length=255)
    evidence_key: str | None = Field(default=None, max_length=255)

    _normalize_plate = field_validator("detected_plate")(normalize_plate)


class AccessEventResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: EventType
    user_id: int | None
    vehicle_id: int | None
    detected_plate: str | None
    face_score: float | None
    plate_score: float | None
    decision: Decision
    reason: str | None
    evidence_key: str | None

    model_config = ConfigDict(from_attributes=True)


class AuthorizationRequest(BaseModel):
    user_id: int
    detected_plate: str
    event_type: EventType
    face_score: float | None = Field(default=None, ge=0, le=1)
    plate_score: float | None = Field(default=None, ge=0, le=1)
    evidence_key: str | None = Field(default=None, max_length=255)

    _normalize_plate = field_validator("detected_plate")(normalize_plate)


class AuthorizationResponse(BaseModel):
    decision: Decision
    reason: str
    user_id: int
    vehicle_id: int | None
    detected_plate: str
