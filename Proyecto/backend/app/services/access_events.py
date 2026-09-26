from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.access_event import AccessEvent
from backend.app.models.user import User
from backend.app.models.vehicle import Vehicle
from backend.app.schemas.access_event import AccessEventCreate


def create_access_event(db: Session, event_data: AccessEventCreate) -> AccessEvent:
    if event_data.user_id is not None and db.get(User, event_data.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    if event_data.vehicle_id is not None and db.get(Vehicle, event_data.vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    values = event_data.model_dump(exclude={"timestamp"})
    if event_data.timestamp is not None:
        values["timestamp"] = event_data.timestamp
    event = AccessEvent(**values)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_access_events(db: Session) -> list[AccessEvent]:
    query = select(AccessEvent).order_by(AccessEvent.timestamp.desc(), AccessEvent.id.desc())
    return list(db.scalars(query).all())


def get_access_event(db: Session, event_id: int) -> AccessEvent:
    event = db.get(AccessEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Access event not found")
    return event
