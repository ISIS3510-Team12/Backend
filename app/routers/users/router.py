from datetime import UTC, datetime
from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies.auth import FirebaseUser, CurrentUser
from app.models import User, UserPreferences
from app.core.dependencies.services import UserServiceDep
from app.schemas import UserCreate, UserPreferencesUpdate

router = APIRouter(
    prefix="/users",
)

@router.post(
    "/create_user",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreate,
    firebase_user: FirebaseUser,
    service: UserServiceDep,
) -> User:
    """
    Create an application user from a verified Firebase identity.
    """
    uid = firebase_user.get("uid")

    if not isinstance(uid, str) or not uid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Firebase user must have a UID",
        )

    if service.get_user_by_id(uid) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    auth_provider = service.get_auth_provider(firebase_user)

    user = User(
            user_id=uid,
            first_name=request.first_name,
            last_name=request.last_name,
            major=request.major,
            auth_provider=auth_provider,
            last_active_at=datetime.now(UTC),
        )
    
    persisted_user = service.create_user(user)
    user_preferences = UserPreferences(user_id=persisted_user.user_id, push_enabled=True)
    service.create_user_preferences(persisted_user.user_id, user_preferences)
    return persisted_user


@router.post(
    "/create-db-user",
    status_code=status.HTTP_201_CREATED,
)
def create_db_user(
    uid: str,
    service: UserServiceDep,
) -> User:
    """
    Create a sample user for the database.
    """

    auth_provider = service.get_auth_provider({"firebase": {"sign_in_provider": "firebase"}})

    user = User(
            user_id=uid,
            first_name="",
            last_name="",
            major="",
            auth_provider=auth_provider,
            last_active_at=datetime.now(UTC),
        )
    
    persisted_user = service.create_user(user)
    return persisted_user

@router.get(
    "/current_user",
)
def get_current_user(current_user: CurrentUser) -> User:
    """
    Get the current authenticated application user.
    - Return User
    - Return UserPreferences
    """
    return current_user


@router.get(
    "/current_db_user",
)
def get_current_db_user(
    service: UserServiceDep,
    user_id: str,
) -> Any:
    """
    Retrieve the current authenticated application user.
    """
    persisted_user = service.get_user_by_id(user_id)
    if persisted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    preferences = service.get_user_preferences_by_user_id(user_id)
    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )
    user = persisted_user.model_dump()
    user["preferences"] = preferences.model_dump()
    return user
    



