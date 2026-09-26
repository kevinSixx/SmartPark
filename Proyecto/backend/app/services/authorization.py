from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.access_event import AccessEvent
from backend.app.models.permission import Permission
from backend.app.models.user import User
from backend.app.models.vehicle import Vehicle
from backend.app.schemas.access_event import AuthorizationRequest, AuthorizationResponse


def authorize_access(
    db: Session, request: AuthorizationRequest
) -> AuthorizationResponse:
    user = db.get(User, request.user_id)
    vehicle = db.scalar(select(Vehicle).where(Vehicle.plate == request.detected_plate))

    if user is None:
        decision = "REJECTED"
        reason = "User not found"
    elif user.status != "ACTIVE":
        decision = "REJECTED"
        reason = "User is inactive"
    elif vehicle is None:
        decision = "REJECTED"
        reason = "Plate is not registered"
    elif vehicle.user_id != user.id:
        decision = "REVIEW"
        reason = "Vehicle is associated with another user"
    elif vehicle.status != "ACTIVE":
        decision = "REJECTED"
        reason = "Vehicle is inactive"
    else:
        permission = db.scalar(
            select(Permission).where(
                Permission.user_id == user.id,
                Permission.vehicle_id == vehicle.id,
            )
        )
        now = datetime.now(timezone.utc)
        if permission is None:
            decision = "REJECTED"
            reason = "No permission exists for this user and vehicle"
        elif not permission.active:
            decision = "REJECTED"
            reason = "Permission is inactive"
        elif permission.valid_from is not None and now < permission.valid_from:
            decision = "REJECTED"
            reason = "Permission is not valid yet"
        elif permission.valid_to is not None and now > permission.valid_to:
            decision = "REJECTED"
            reason = "Permission has expired"
        else:
            decision = "AUTHORIZED"
            reason = "Active permission found for user and vehicle"

    event = AccessEvent(
        event_type=request.event_type,
        user_id=user.id if user is not None else None,
        vehicle_id=vehicle.id if vehicle is not None else None,
        detected_plate=request.detected_plate,
        face_score=request.face_score,
        plate_score=request.plate_score,
        decision=decision,
        reason=reason,
        evidence_key=request.evidence_key,
    )
    db.add(event)
    db.commit()

    return AuthorizationResponse(
        decision=decision,
        reason=reason,
        user_id=request.user_id,
        vehicle_id=vehicle.id if vehicle is not None else None,
        detected_plate=request.detected_plate,
    )
