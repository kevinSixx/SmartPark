import math
import os

import httpx

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.models.face_profile import FaceProfile
from backend.app.models.face_sample import FaceSample
from backend.app.models.user import User

from backend.app.services.s3_storage import (
    build_face_sample_key,
    create_presigned_url,
    delete_object,
    upload_bytes,
)


# ============================================================
# CONFIGURACION
# ============================================================

AI_BASE_URL = os.getenv(
    "AI_BASE_URL",
    "http://54.221.14.254:8001"
)

AI_FACE_ENROLL_URL = (
    f"{AI_BASE_URL}/face/enroll"
)

FACE_MATCH_THRESHOLD = float(
    os.getenv(
        "FACE_MATCH_THRESHOLD",
        "0.70"
    )
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MIN_ENROLLMENT_IMAGES = 3

MAX_ENROLLMENT_IMAGES = 5

MAX_IMAGE_SIZE_BYTES = (
    10
    *
    1024
    *
    1024
)


# ============================================================
# USUARIO
# ============================================================

def get_existing_user(
    db: Session,
    user_id: int
) -> User:

    user = db.get(
        User,
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ============================================================
# VALIDAR Y LEER FOTOS
# ============================================================

async def read_enrollment_images(
    images: list[UploadFile]
) -> list[dict]:

    if not (
        MIN_ENROLLMENT_IMAGES
        <=
        len(images)
        <=
        MAX_ENROLLMENT_IMAGES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Face enrollment requires "
                "between 3 and 5 images"
            )
        )

    prepared_images = []


    for index, image in enumerate(
        images
    ):

        content_type = (
            image.content_type
            or
            ""
        )

        if (
            content_type
            not in
            ALLOWED_CONTENT_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Image {index + 1} has "
                    "an unsupported content type"
                )
            )


        data = await image.read()


        if not data:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Image {index + 1} "
                    "is empty"
                )
            )


        if (
            len(data)
            >
            MAX_IMAGE_SIZE_BYTES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Image {index + 1} "
                    "exceeds 10 MB"
                )
            )


        prepared_images.append({
            "index":
                index,

            "filename":
                image.filename
                or
                f"face-{index + 1}.jpg",

            "content_type":
                content_type,

            "data":
                data
        })


    return prepared_images


# ============================================================
# LLAMAR IA
# ============================================================

async def request_face_embedding(
    prepared_images: list[dict]
) -> dict:

    files = []


    for item in prepared_images:

        files.append(
            (
                "images",

                (
                    item["filename"],
                    item["data"],
                    item["content_type"]
                )
            )
        )


    try:

        async with httpx.AsyncClient(
            timeout=180.0
        ) as client:

            response = await client.post(
                AI_FACE_ENROLL_URL,
                files=files
            )


    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Could not connect to "
                "SmartPark AI"
            )
        ) from exc


    if response.status_code >= 400:

        try:

            ai_error = response.json()

        except Exception:

            ai_error = {
                "detail":
                    response.text
            }


        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message":
                    "AI face enrollment failed",

                "ai_response":
                    ai_error
            }
        )


    try:

        result = response.json()

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "SmartPark AI returned "
                "an invalid response"
            )
        ) from exc


    embedding = result.get(
        "embedding"
    )

    embedding_dimension = int(
        result.get(
            "embedding_dimension",
            0
        )
        or
        0
    )


    if (
        not isinstance(
            embedding,
            list
        )
        or
        not embedding
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "SmartPark AI did not "
                "return a valid embedding"
            )
        )


    if (
        embedding_dimension
        !=
        len(embedding)
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Embedding dimension "
                "does not match vector size"
            )
        )


    return result


# ============================================================
# ENROLAR
# ============================================================

async def enroll_face_profile(
    db: Session,
    user_id: int,
    images: list[UploadFile]
) -> dict:

    user = get_existing_user(
        db,
        user_id
    )


    # ========================================================
    # 1. LEER IMAGENES
    # ========================================================

    prepared_images = (
        await read_enrollment_images(
            images
        )
    )


    # ========================================================
    # 2. IA
    # ========================================================

    ai_result = (
        await request_face_embedding(
            prepared_images
        )
    )


    embedding = [
        float(value)
        for value in ai_result[
            "embedding"
        ]
    ]


    embedding_dimension = len(
        embedding
    )


    model_name = (
        ai_result.get(
            "model_name"
        )
        or
        "ArcFace"
    )


    detector_backend = (
        ai_result.get(
            "detector_backend"
        )
        or
        "retinaface"
    )


    sample_results = (
        ai_result.get(
            "sample_results"
        )
        or
        []
    )


    quality_by_index = {}


    for item in sample_results:

        try:

            quality_by_index[
                int(item["index"])
            ] = float(
                item.get(
                    "quality_score",
                    0.0
                )
            )

        except Exception:

            continue


    # ========================================================
    # 3. PERFIL ANTERIOR
    # ========================================================

    old_profile = db.scalar(
        select(
            FaceProfile
        ).where(
            FaceProfile.user_id
            ==
            user_id
        )
    )


    old_samples = list(
        db.scalars(
            select(
                FaceSample
            ).where(
                FaceSample.user_id
                ==
                user_id
            )
        ).all()
    )


    old_s3_keys = [
        sample.s3_key
        for sample in old_samples
    ]


    # ========================================================
    # 4. SUBIR NUEVAS FOTOS A S3
    # ========================================================

    uploaded_keys = []

    new_sample_data = []


    try:

        for item in prepared_images:

            key = (
                build_face_sample_key(

                    user_id=
                        user_id,

                    filename=
                        item["filename"],

                    content_type=
                        item["content_type"]
                )
            )


            upload_bytes(
                data=
                    item["data"],

                key=
                    key,

                content_type=
                    item["content_type"]
            )


            uploaded_keys.append(
                key
            )


            new_sample_data.append({
                "s3_key":
                    key,

                "original_filename":
                    item["filename"],

                "content_type":
                    item["content_type"],

                "quality_score":
                    quality_by_index.get(
                        item["index"]
                    )
            })


    except Exception:

        for key in uploaded_keys:

            delete_object(
                key
            )

        raise


    # ========================================================
    # 5. BASE DE DATOS
    # ========================================================

    try:

        # ----------------------------------------------------
        # Eliminar muestras anteriores
        # ----------------------------------------------------

        for sample in old_samples:

            db.delete(
                sample
            )


        # ----------------------------------------------------
        # Crear / actualizar perfil
        # ----------------------------------------------------

        if old_profile is None:

            profile = FaceProfile(

                user_id=
                    user_id,

                embedding=
                    embedding,

                embedding_dimension=
                    embedding_dimension,

                model_name=
                    model_name,

                detector_backend=
                    detector_backend,

                is_active=
                    True
            )

            db.add(
                profile
            )

        else:

            profile = old_profile

            profile.embedding = (
                embedding
            )

            profile.embedding_dimension = (
                embedding_dimension
            )

            profile.model_name = (
                model_name
            )

            profile.detector_backend = (
                detector_backend
            )

            profile.is_active = True


        # ----------------------------------------------------
        # Nuevas muestras
        # ----------------------------------------------------

        for item in new_sample_data:

            sample = FaceSample(

                user_id=
                    user_id,

                s3_key=
                    item["s3_key"],

                original_filename=
                    item[
                        "original_filename"
                    ],

                content_type=
                    item[
                        "content_type"
                    ],

                quality_score=
                    item[
                        "quality_score"
                    ],

                is_active=
                    True
            )

            db.add(
                sample
            )


        db.commit()

        db.refresh(
            profile
        )


    except SQLAlchemyError as exc:

        db.rollback()


        # Limpiar las nuevas imágenes,
        # porque la BD no pudo confirmar.
        for key in uploaded_keys:

            delete_object(
                key
            )


        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save face "
                "profile in database"
            )
        ) from exc


    # ========================================================
    # 6. LIMPIAR ANTIGUAS DE S3
    # ========================================================

    for key in old_s3_keys:

        delete_object(
            key
        )


    # ========================================================
    # 7. RESPUESTA
    # ========================================================

    return {
        "status":
            "enrolled",

        "user_id":
            user.id,

        "person":
            user.name,

        "profile_id":
            profile.id,

        "samples_used":
            len(
                prepared_images
            ),

        "embedding_dimension":
            profile.embedding_dimension,

        "model_name":
            profile.model_name,

        "detector_backend":
            profile.detector_backend
    }


# ============================================================
# OBTENER PERFIL
# ============================================================

def get_face_profile(
    db: Session,
    user_id: int
) -> dict:

    get_existing_user(
        db,
        user_id
    )


    profile = db.scalar(
        select(
            FaceProfile
        ).where(
            FaceProfile.user_id
            ==
            user_id
        )
    )


    if profile is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Face profile not found"
            )
        )


    samples_count = len(
        list(
            db.scalars(
                select(
                    FaceSample
                ).where(
                    FaceSample.user_id
                    ==
                    user_id
                )
            ).all()
        )
    )


    return {
        "id":
            profile.id,

        "user_id":
            profile.user_id,

        "embedding_dimension":
            profile.embedding_dimension,

        "model_name":
            profile.model_name,

        "detector_backend":
            profile.detector_backend,

        "is_active":
            profile.is_active,

        "samples_count":
            samples_count,

        "created_at":
            profile.created_at,

        "updated_at":
            profile.updated_at
    }


# ============================================================
# LISTAR MUESTRAS
# ============================================================

def list_face_samples(
    db: Session,
    user_id: int
) -> list[dict]:

    get_existing_user(
        db,
        user_id
    )


    samples = list(
        db.scalars(

            select(
                FaceSample
            )

            .where(
                FaceSample.user_id
                ==
                user_id
            )

            .order_by(
                FaceSample.id
            )

        ).all()
    )


    result = []


    for sample in samples:

        result.append({
            "id":
                sample.id,

            "user_id":
                sample.user_id,

            "s3_key":
                sample.s3_key,

            "original_filename":
                sample.original_filename,

            "content_type":
                sample.content_type,

            "quality_score":
                sample.quality_score,

            "is_active":
                sample.is_active,

            "created_at":
                sample.created_at,

            "url":
                create_presigned_url(
                    sample.s3_key
                )
        })


    return result


# ============================================================
# ELIMINAR PERFIL
# ============================================================

def delete_face_profile(
    db: Session,
    user_id: int
) -> dict:

    get_existing_user(
        db,
        user_id
    )


    profile = db.scalar(
        select(
            FaceProfile
        ).where(
            FaceProfile.user_id
            ==
            user_id
        )
    )


    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="Face profile not found"
        )


    samples = list(
        db.scalars(
            select(
                FaceSample
            ).where(
                FaceSample.user_id
                ==
                user_id
            )
        ).all()
    )


    keys = [
        item.s3_key
        for item in samples
    ]


    try:

        for sample in samples:

            db.delete(
                sample
            )


        db.delete(
            profile
        )


        db.commit()


    except SQLAlchemyError as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not delete "
                "face profile"
            )
        ) from exc


    for key in keys:

        delete_object(
            key
        )


    return {
        "status":
            "deleted",

        "user_id":
            user_id
    }


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    a: list[float],
    b: list[float]
) -> float:

    if len(a) != len(b):

        return -1.0


    dot_product = sum(
        x * y
        for x, y in zip(
            a,
            b
        )
    )


    norm_a = math.sqrt(
        sum(
            x * x
            for x in a
        )
    )


    norm_b = math.sqrt(
        sum(
            y * y
            for y in b
        )
    )


    if (
        norm_a == 0.0
        or
        norm_b == 0.0
    ):

        return -1.0


    return (
        dot_product
        /
        (
            norm_a
            *
            norm_b
        )
    )


# ============================================================
# MATCH FACIAL
# ============================================================

def match_face_embedding(
    db: Session,
    embedding: list[float],
    threshold: float | None = None
) -> dict:

    selected_threshold = (
        threshold
        if threshold is not None
        else FACE_MATCH_THRESHOLD
    )


    profiles = list(
        db.scalars(

            select(
                FaceProfile
            )

            .where(
                FaceProfile.is_active
                .is_(True)
            )

        ).all()
    )


    best_profile = None

    best_similarity = -1.0


    for profile in profiles:

        stored_embedding = [
            float(value)
            for value
            in profile.embedding
        ]


        similarity = (
            cosine_similarity(
                embedding,
                stored_embedding
            )
        )


        if (
            similarity
            >
            best_similarity
        ):

            best_similarity = (
                similarity
            )

            best_profile = (
                profile
            )


    if (
        best_profile is None
        or
        best_similarity
        <
        selected_threshold
    ):

        return {
            "matched":
                False,

            "user_id":
                None,

            "person":
                None,

            "institutional_id":
                None,

            "similarity":
                (
                    best_similarity
                    if best_similarity >= 0
                    else None
                ),

            "threshold":
                selected_threshold
        }


    user = db.get(
        User,
        best_profile.user_id
    )


    if (
        user is None
        or
        user.status != "ACTIVE"
    ):

        return {
            "matched":
                False,

            "user_id":
                None,

            "person":
                None,

            "institutional_id":
                None,

            "similarity":
                best_similarity,

            "threshold":
                selected_threshold
        }


    return {
        "matched":
            True,

        "user_id":
            user.id,

        "person":
            user.name,

        "institutional_id":
            user.institutional_id,

        "similarity":
            best_similarity,

        "threshold":
            selected_threshold
    }