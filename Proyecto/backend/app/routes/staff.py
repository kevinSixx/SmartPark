from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.models.staff_account import (
    StaffAccount,
)

from backend.app.schemas.staff_account import (
    StaffAccountCreate,
    StaffAccountResponse,
    StaffAccountUpdate,
)

from backend.app.services.auth import (
    require_admin,
)

from backend.app.services.staff_accounts import (
    create_staff_account,
    get_staff_account,
    list_staff_accounts,
    update_staff_account,
)


router = APIRouter(
    prefix="/api/v1/staff",
    tags=["Staff"],
)


# ============================================================
# LISTAR PERSONAL
# SOLO ADMIN
# ============================================================

@router.get(
    "",
    response_model=list[StaffAccountResponse],
)
def list_staff(
    db: Session = Depends(get_db),

    current_admin: StaffAccount
        = Depends(require_admin),
):

    return list_staff_accounts(
        db
    )


# ============================================================
# OBTENER PERSONAL
# SOLO ADMIN
# ============================================================

@router.get(
    "/{staff_id}",
    response_model=StaffAccountResponse,
)
def get_staff(
    staff_id: int,

    db: Session = Depends(get_db),

    current_admin: StaffAccount
        = Depends(require_admin),
):

    return get_staff_account(
        db,
        staff_id,
    )


# ============================================================
# CREAR ADMIN / GUARD
# SOLO ADMIN
# ============================================================

@router.post(
    "",
    response_model=StaffAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(
    staff_data: StaffAccountCreate,

    db: Session = Depends(get_db),

    current_admin: StaffAccount
        = Depends(require_admin),
):

    return create_staff_account(
        db,
        staff_data,
    )


# ============================================================
# ACTUALIZAR PERSONAL
# SOLO ADMIN
# ============================================================

@router.patch(
    "/{staff_id}",
    response_model=StaffAccountResponse,
)
def update_staff(
    staff_id: int,

    staff_data: StaffAccountUpdate,

    db: Session = Depends(get_db),

    current_admin: StaffAccount
        = Depends(require_admin),
):

    return update_staff_account(
        db,
        staff_id,
        staff_data,
    )