from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, status
from firebase_admin import auth
from pydantic import BaseModel, StringConstraints
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import DatabaseSession, FirebaseUser, CurrentUser
from app.models import User


router = APIRouter(
    prefix="/auth",
)

class UserCreateRequest(BaseModel):
    first_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
    ]
    last_name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
    ]
    major: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=150),
    ]


@router.post("/check_token")
def check_token(token: str):
    """
    Verify a Firebase ID token and return the decoded token.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        return {"error": "Invalid ID token"}


@router.post(
    "/create_user",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreateRequest,
    firebase_user: FirebaseUser,
    db: DatabaseSession,
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

    if db.get(User, uid) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    auth_provider = _get_auth_provider(firebase_user)
    # TODO: In user add email field
    user = User(
        user_id=uid,
        first_name=request.first_name,
        last_name=request.last_name,
        major=request.major,
        auth_provider=auth_provider,
        last_active_at=datetime.now(UTC),
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this Firebase UID or email already exists",
        ) from error

    db.refresh(user)
    return user

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
