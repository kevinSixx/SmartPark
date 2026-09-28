import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.models.staff_account import (
    StaffAccount,
)

from backend.app.services.staff_accounts import (
    get_staff_by_username,
    verify_password,
)


# ============================================================
# CONFIGURACION JWT
# ============================================================

AUTH_SECRET_KEY = os.getenv(
    "AUTH_SECRET_KEY",
    ""
)

AUTH_TOKEN_MINUTES = int(
    os.getenv(
        "AUTH_TOKEN_MINUTES",
        "480"
    )
)

AUTH_ALGORITHM = "HS256"


if not AUTH_SECRET_KEY:

    raise RuntimeError(
        "AUTH_SECRET_KEY is not configured"
    )


# ============================================================
# BEARER
# ============================================================

security = HTTPBearer(
    auto_error=True
)


# ============================================================
# AUTENTICAR USUARIO
# ============================================================

def authenticate_staff(
    db: Session,
    username: str,
    password: str,
) -> StaffAccount:

    staff = get_staff_by_username(
        db,
        username,
    )

    if staff is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Usuario o contraseña incorrectos"
            ),
        )

    if not verify_password(
        password,
        staff.password_hash,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Usuario o contraseña incorrectos"
            ),
        )

    if not staff.active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "La cuenta está desactivada"
            ),
        )

    return staff


# ============================================================
# CREAR TOKEN
# ============================================================

def create_access_token(
    staff: StaffAccount,
) -> tuple[str, int]:

    expires_in = (
        AUTH_TOKEN_MINUTES * 60
    )

    expires_at = (
        datetime.now(
            timezone.utc
        )
        +
        timedelta(
            minutes=AUTH_TOKEN_MINUTES
        )
    )

    payload = {

        "sub":
            str(staff.id),

        "username":
            staff.username,

        "role":
            staff.role,

        "exp":
            expires_at,

        "iat":
            datetime.now(
                timezone.utc
            ),
    }

    token = jwt.encode(
        payload,
        AUTH_SECRET_KEY,
        algorithm=AUTH_ALGORITHM,
    )

    return (
        token,
        expires_in,
    )


# ============================================================
# DECODIFICAR TOKEN
# ============================================================

def decode_access_token(
    token: str,
) -> dict:

    try:

        return jwt.decode(
            token,
            AUTH_SECRET_KEY,
            algorithms=[
                AUTH_ALGORITHM
            ],
        )

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


# ============================================================
# USUARIO ACTUAL
# ============================================================

def get_current_staff(
    credentials:
        HTTPAuthorizationCredentials
        = Depends(security),

    db: Session
        = Depends(get_db),

) -> StaffAccount:

    payload = decode_access_token(
        credentials.credentials
    )

    staff_id = payload.get(
        "sub"
    )

    if staff_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    try:

        staff_id_int = int(
            staff_id
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    staff = db.get(
        StaffAccount,
        staff_id_int,
    )

    if staff is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Cuenta no encontrada"
            ),
        )

    if not staff.active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Cuenta desactivada"
            ),
        )

    return staff


# ============================================================
# SOLO ADMIN
# ============================================================

def require_admin(
    current_staff: StaffAccount
        = Depends(get_current_staff),
) -> StaffAccount:

    if current_staff.role != "ADMIN":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Se requiere rol ADMIN"
            ),
        )

    return current_staff