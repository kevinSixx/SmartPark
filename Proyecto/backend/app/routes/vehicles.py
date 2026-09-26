from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from backend.app.services.vehicles import (
    create_vehicle,
    get_vehicle,
    list_user_vehicles,
    list_vehicles,
    update_vehicle,
)


router = APIRouter(tags=["Vehicles"])


@router.post("/vehicles", response_model=VehicleResponse, status_code=201)
def register_vehicle(
    vehicle_data: VehicleCreate, db: Session = Depends(get_db)
):
    return create_vehicle(db, vehicle_data)


@router.get("/vehicles", response_model=list[VehicleResponse])
def read_vehicles(db: Session = Depends(get_db)):
    return list_vehicles(db)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def read_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return get_vehicle(db, vehicle_id)


@router.get("/users/{user_id}/vehicles", response_model=list[VehicleResponse])
def read_user_vehicles(user_id: int, db: Session = Depends(get_db)):
    return list_user_vehicles(db, user_id)


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def edit_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
):
    return update_vehicle(db, vehicle_id, vehicle_data)
