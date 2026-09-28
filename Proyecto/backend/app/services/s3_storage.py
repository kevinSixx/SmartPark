import os
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status


# ============================================================
# CONFIGURACION
# ============================================================

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)

SMARTPARK_MEDIA_BUCKET = os.getenv(
    "SMARTPARK_MEDIA_BUCKET",
    "smartpark-uce-media-573672769830"
)


# ============================================================
# CLIENTE S3
# ============================================================

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)


# ============================================================
# EXTENSION
# ============================================================

def get_extension(
    filename: str | None,
    content_type: str | None
) -> str:

    if content_type == "image/jpeg":
        return ".jpg"

    if content_type == "image/png":
        return ".png"

    if content_type == "image/webp":
        return ".webp"

    if filename:

        suffix = Path(filename).suffix.lower()

        if suffix in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }:

            if suffix == ".jpeg":
                return ".jpg"

            return suffix

    return ".jpg"


# ============================================================
# GENERAR KEY PARA ROSTRO
# ============================================================

def build_face_sample_key(
    user_id: int,
    filename: str | None,
    content_type: str | None
) -> str:

    extension = get_extension(
        filename,
        content_type
    )

    object_id = uuid.uuid4().hex

    return (
        f"users/{user_id}/face/"
        f"{object_id}{extension}"
    )


# ============================================================
# SUBIR
# ============================================================

def upload_bytes(
    data: bytes,
    key: str,
    content_type: str
) -> None:

    try:

        s3_client.put_object(
            Bucket=SMARTPARK_MEDIA_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type
        )

    except (
        BotoCoreError,
        ClientError
    ) as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not upload image to S3"
        ) from exc


# ============================================================
# ELIMINAR
# ============================================================

def delete_object(
    key: str
) -> None:

    try:

        s3_client.delete_object(
            Bucket=SMARTPARK_MEDIA_BUCKET,
            Key=key
        )

    except (
        BotoCoreError,
        ClientError
    ):

        # No rompemos una operacion de BD solamente porque
        # falle la limpieza de una evidencia antigua.
        pass


# ============================================================
# URL TEMPORAL
# ============================================================

def create_presigned_url(
    key: str,
    expires_in: int = 300
) -> str:

    try:

        return s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket":
                    SMARTPARK_MEDIA_BUCKET,

                "Key":
                    key
            },
            ExpiresIn=expires_in
        )

    except (
        BotoCoreError,
        ClientError
    ) as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate S3 URL"
        ) from exc