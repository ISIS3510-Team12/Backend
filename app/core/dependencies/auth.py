from __future__ import annotations
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from app.models import User
from app.core.dependencies.database import DatabaseSession

bearer_scheme = HTTPBearer(auto_error=False)

"""
Auth dependencies for the application, including Firebase user verification
and current user.
"""

def get_firebase_user_from_token(
    token: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> dict[str, Any]:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return auth.verify_id_token(token.credentials)
    except (
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def get_current_user(
    firebase_user: FirebaseUser,
    db: DatabaseSession,
) -> User:
    user = db.get(User, firebase_user["uid"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Application user does not exist",
        )

    return user

FirebaseUser = Annotated[
    dict[str, Any],
    Depends(get_firebase_user_from_token),
]

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]