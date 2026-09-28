import hashlib
import hmac
import secrets

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.staff_account import StaffAccount
from backend.app.schemas.staff_account import (
    StaffAccountCreate,
    StaffAccountUpdate,
)


PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256"
        f"${PASSWORD_ITERATIONS}"
        f"${salt.hex()}"
        f"${password_hash.hex()}"
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    try:
        algorithm, iterations, salt_hex, hash_hex = (
            stored_hash.split("$", 3)
        )

        if algorithm != "pbkdf2_sha256":
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )

        return hmac.compare_digest(
            calculated_hash.hex(),
            hash_hex,
        )

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):
        return False


def create_staff_account(
    db: Session,
    staff_data: StaffAccountCreate,
) -> StaffAccount:

    existing = db.scalar(
        select(StaffAccount).where(
            StaffAccount.username
            == staff_data.username
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    staff = StaffAccount(
        full_name=staff_data.full_name,
        username=staff_data.username,
        password_hash=hash_password(
            staff_data.password
        ),
        role=staff_data.role,
        active=staff_data.active,
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return staff


def list_staff_accounts(
    db: Session,
) -> list[StaffAccount]:

    query = (
        select(StaffAccount)
        .order_by(
            StaffAccount.full_name.asc(),
            StaffAccount.id.asc(),
        )
    )

    return list(
        db.scalars(query).all()
    )


def get_staff_account(
    db: Session,
    staff_id: int,
) -> StaffAccount:

    staff = db.get(
        StaffAccount,
        staff_id,
    )

    if staff is None:
        raise HTTPException(
            status_code=404,
            detail="Staff account not found",
        )

    return staff


def get_staff_by_username(
    db: Session,
    username: str,
) -> StaffAccount | None:

    normalized_username = (
        username
        .strip()
        .lower()
    )

    return db.scalar(
        select(StaffAccount).where(
            StaffAccount.username
            == normalized_username
        )
    )


def update_staff_account(
    db: Session,
    staff_id: int,
    staff_data: StaffAccountUpdate,
) -> StaffAccount:

    staff = get_staff_account(
        db,
        staff_id,
    )

    update_data = (
        staff_data.model_dump(
            exclude_unset=True
        )
    )

    password = update_data.pop(
        "password",
        None,
    )

    for field, value in update_data.items():
        setattr(
            staff,
            field,
            value,
        )

    if password is not None:
        staff.password_hash = (
            hash_password(password)
        )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return staff