from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.permission import Permission
from backend.app.models.user import User
from backend.app.models.vehicle import Vehicle
from backend.app.schemas.permission import PermissionCreate, PermissionUpdate


def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
    if db.get(User, permission_data.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    vehicle = db.get(Vehicle, permission_data.vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.user_id != permission_data.user_id:
        raise HTTPException(
            status_code=409,
            detail="The vehicle is not associated with this user",
        )

    permission = Permission(**permission_data.model_dump())
    db.add(permission)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A permission for this user and vehicle already exists",
        ) from exc
    db.refresh(permission)
    return permission


def list_permissions(db: Session) -> list[Permission]:
    return list(db.scalars(select(Permission).order_by(Permission.id)).all())


def get_permission(db: Session, permission_id: int) -> Permission:
    permission = db.get(Permission, permission_id)
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


def update_permission(
    db: Session, permission_id: int, permission_data: PermissionUpdate
) -> Permission:
    permission = get_permission(db, permission_id)
    changes = permission_data.model_dump(exclude_unset=True)
    valid_from = changes.get("valid_from", permission.valid_from)
    valid_to = changes.get("valid_to", permission.valid_to)
    if valid_from is not None and valid_to is not None and valid_to < valid_from:
        raise HTTPException(
            status_code=422,
            detail="valid_to must be greater than or equal to valid_from",
        )
    for field, value in changes.items():
        setattr(permission, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail="Invalid permission data") from exc
    db.refresh(permission)
    return permission
