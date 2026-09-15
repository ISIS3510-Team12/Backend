from __future__ import annotations
from app.core.config import settings
import boto3
from functools import lru_cache
from typing import TYPE_CHECKING, Annotated
import firebase_admin
from firebase_admin import App, credentials
from app.auth.auth import get_firebase_user_from_token
from fastapi import Depends

if TYPE_CHECKING:
    from types_boto3_s3.service_resource import S3ServiceResource
    from types_boto3_s3.client import S3Client


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


FirebaseUser = Annotated[
    dict,
    Depends(get_firebase_user_from_token),
]

s3_client = get_s3_client()
s3_resource = get_s3_resource()
