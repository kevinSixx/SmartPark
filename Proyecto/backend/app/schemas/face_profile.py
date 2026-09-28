from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# FACE PROFILE
# ============================================================

class FaceProfileResponse(BaseModel):

    id: int
    user_id: int

    embedding_dimension: int

    model_name: str

    detector_backend: str

    is_active: bool

    samples_count: int

    created_at: datetime

    updated_at: datetime


# ============================================================
# ENROLLMENT
# ============================================================

class FaceEnrollmentResponse(BaseModel):

    status: str

    user_id: int

    person: str

    profile_id: int

    samples_used: int

    embedding_dimension: int

    model_name: str

    detector_backend: str


# ============================================================
# SAMPLE
# ============================================================

class FaceSampleResponse(BaseModel):

    id: int

    user_id: int

    s3_key: str

    original_filename: str | None

    content_type: str | None

    quality_score: float | None

    is_active: bool

    created_at: datetime

    url: str | None = None


# ============================================================
# MATCH
# ============================================================

class FaceMatchRequest(BaseModel):

    embedding: list[float] = Field(
        min_length=1
    )

    threshold: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0
    )


class FaceMatchResponse(BaseModel):

    matched: bool

    user_id: int | None = None

    person: str | None = None

    institutional_id: str | None = None

    similarity: float | None = None

    threshold: float