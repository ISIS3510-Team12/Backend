from datetime import UTC, datetime
from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies.auth import FirebaseUser, CurrentUser
from app.models import User
from app.core.dependencies.services import UserServiceDep
from app.schemas import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post(
    "/create_user",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreate,
    firebase_user: FirebaseUser,
    service: UserServiceDep,
):
    """
    Create an application user from a verified Firebase identity.
    """
    uid = service.check_user_firebase_uid(firebase_user)
    email = service.check_user_firebase_email(firebase_user)
    auth_provider = service.get_auth_provider(firebase_user)

    user = User(
            user_id=uid,
            email=email,
            first_name=request.first_name,
            last_name=request.last_name,
            major=request.major,
            auth_provider=auth_provider,
            last_active_at=datetime.now(UTC),
        )
    persisted_user = service.create_user(user)
    return persisted_user


@router.get(
    "/current_user",
)
def get_current_user(current_user: CurrentUser):
    """
    Get the current authenticated application user.
    """
    return current_user






