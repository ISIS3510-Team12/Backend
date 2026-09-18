from __future__ import annotations
import boto3
import firebase_admin
from functools import lru_cache
from typing import Annotated, Any, TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import App, auth, credentials
from sqlmodel import Session
from app.core.config import settings
from app.db import get_db
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)

if TYPE_CHECKING:
    from types_boto3_s3.service_resource import S3ServiceResource
    from types_boto3_s3.client import S3Client


"""

Core dependencies for the application, including database session management,
S3 client and resource initialization, and Firebase authentication.

"""

@lru_cache
def get_s3_client() -> S3Client:
    return boto3.client(
        service_name="s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT,
    )


@lru_cache
def get_s3_resource() -> S3ServiceResource:
    return boto3.resource(
        service_name="s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT,
    )


@lru_cache
def initialize_firebase_app() -> App:
    firebase_credentials = settings.FIREBASE_CREDENTIALS_DATA
    certificate = credentials.Certificate(
        firebase_credentials.model_dump()
    )
    return firebase_admin.initialize_app(certificate)


s3_client = get_s3_client()
s3_resource = get_s3_resource()

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


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

# Use this dependency when creating a user for the first time after verifying the Firebase token
FirebaseUser = Annotated[
    dict[str, Any],
    Depends(get_firebase_user_from_token),
]

# Use this dependency in the endpoints that require the current authenticated user
CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
