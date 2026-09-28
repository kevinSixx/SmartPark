from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.schemas.face_profile import (
    FaceEnrollmentResponse,
    FaceMatchRequest,
    FaceMatchResponse,
    FaceProfileResponse,
    FaceSampleResponse,
)

from backend.app.services.face_profiles import (
    delete_face_profile,
    enroll_face_profile,
    get_face_profile,
    list_face_samples,
    match_face_embedding,
)


router = APIRouter(
    prefix="/face-profiles",
    tags=["Face Profiles"]
)


# ============================================================
# ENROLL
# ============================================================

@router.post(
    "/enroll",
    response_model=FaceEnrollmentResponse,
    status_code=201
)
async def enroll(
    user_id: int = Form(...),
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):

    return await enroll_face_profile(
        db=db,
        user_id=user_id,
        images=images
    )


# ============================================================
# MATCH
# ============================================================

@router.post(
    "/match",
    response_model=FaceMatchResponse
)
def match(
    data: FaceMatchRequest,
    db: Session = Depends(get_db),
):

    return match_face_embedding(
        db=db,
        embedding=data.embedding,
        threshold=data.threshold
    )


# ============================================================
# GET PROFILE
# ============================================================

@router.get(
    "/{user_id}",
    response_model=FaceProfileResponse
)
def read_face_profile(
    user_id: int,
    db: Session = Depends(get_db),
):

    return get_face_profile(
        db,
        user_id
    )


# ============================================================
# SAMPLES
# ============================================================

@router.get(
    "/{user_id}/samples",
    response_model=list[FaceSampleResponse]
)
def read_face_samples(
    user_id: int,
    db: Session = Depends(get_db),
):

    return list_face_samples(
        db,
        user_id
    )


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{user_id}"
)
def remove_face_profile(
    user_id: int,
    db: Session = Depends(get_db),
):

    return delete_face_profile(
        db,
        user_id
    )