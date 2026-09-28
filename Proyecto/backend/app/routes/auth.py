from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.models.staff_account import (
    StaffAccount,
)

from backend.app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
)

from backend.app.services.auth import (
    authenticate_staff,
    create_access_token,
    get_current_staff,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):

    staff = authenticate_staff(
        db,
        login_data.username,
        login_data.password,
    )

    token, expires_in = (
        create_access_token(
            staff
        )
    )

    return LoginResponse(

        access_token=token,

        token_type="bearer",

        expires_in=expires_in,

        user=AuthUserResponse(
            id=staff.id,
            full_name=staff.full_name,
            username=staff.username,
            role=staff.role,
            active=staff.active,
        ),
    )


# ============================================================
# USUARIO AUTENTICADO
# ============================================================

@router.get(
    "/me",
    response_model=AuthUserResponse,
)
def me(
    current_staff: StaffAccount
        = Depends(get_current_staff),
):

    return AuthUserResponse(
        id=current_staff.id,
        full_name=current_staff.full_name,
        username=current_staff.username,
        role=current_staff.role,
        active=current_staff.active,
    )