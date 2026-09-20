from datetime import UTC, datetime
from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies.auth import FirebaseUser, CurrentUser
from app.models import User
from app.core.dependencies.services import UserServiceDep

router = APIRouter(
    prefix="/auth",
)

@router.post(
    "/create_user",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: User,
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

    auth_provider = _get_auth_provider(firebase_user)

    user = User(
            user_id=uid,
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
def get_current_user(current_user: CurrentUser) -> User:
    """
    Retrieve the current authenticated application user.
    """
    return current_user


def _get_auth_provider(firebase_user: dict[str, Any]) -> str:
    firebase_claims = firebase_user.get("firebase")
    if not isinstance(firebase_claims, dict):
        return "firebase"

    sign_in_provider = firebase_claims.get("sign_in_provider")
    if isinstance(sign_in_provider, str) and sign_in_provider:
        return sign_in_provider

    return "firebase"
