from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.user import UserCreate, UserResponse, UserUpdate
from backend.app.services.users import create_user, get_user, list_users, update_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user_data)


@router.get("", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    return update_user(db, user_id, user_data)
