from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.vehicle import Vehicle
from backend.app.schemas.vehicle import VehicleCreate, VehicleUpdate


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")


def create_vehicle(db: Session, vehicle_data: VehicleCreate) -> Vehicle:
    _ensure_user_exists(db, vehicle_data.user_id)
    vehicle = Vehicle(**vehicle_data.model_dump())
    db.add(vehicle)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this plate already exists",
        ) from exc
    db.refresh(vehicle)
    return vehicle


def list_vehicles(db: Session) -> list[Vehicle]:
    return list(db.scalars(select(Vehicle).order_by(Vehicle.id)).all())


def list_user_vehicles(db: Session, user_id: int) -> list[Vehicle]:
    _ensure_user_exists(db, user_id)
    query = select(Vehicle).where(Vehicle.user_id == user_id).order_by(Vehicle.id)
    return list(db.scalars(query).all())


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def update_vehicle(db: Session, vehicle_id: int, vehicle_data: VehicleUpdate) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    changes = vehicle_data.model_dump(exclude_unset=True)
    if "user_id" in changes:
        _ensure_user_exists(db, changes["user_id"])
    for field, value in changes.items():
        setattr(vehicle, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this plate already exists",
        ) from exc
    db.refresh(vehicle)
    return vehicle
