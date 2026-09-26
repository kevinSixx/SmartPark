from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.permission import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)
from backend.app.services.permissions import (
    create_permission,
    get_permission,
    list_permissions,
    update_permission,
)


router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("", response_model=PermissionResponse, status_code=201)
def register_permission(
    permission_data: PermissionCreate, db: Session = Depends(get_db)
):
    return create_permission(db, permission_data)


@router.get("", response_model=list[PermissionResponse])
def read_permissions(db: Session = Depends(get_db)):
    return list_permissions(db)


@router.get("/{permission_id}", response_model=PermissionResponse)
def read_permission(permission_id: int, db: Session = Depends(get_db)):
    return get_permission(db, permission_id)


@router.patch("/{permission_id}", response_model=PermissionResponse)
def edit_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
):
    return update_permission(db, permission_id, permission_data)
