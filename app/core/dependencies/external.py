from __future__ import annotations
import boto3
import firebase_admin
from functools import lru_cache
from typing import TYPE_CHECKING
from firebase_admin import App, credentials
from app.core.config import settings


if TYPE_CHECKING:
    from types_boto3_s3.client import S3Client


"""
External dependencies for the application, 
S3 client and Firebase authentication initialization.
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
def initialize_firebase_app() -> App:
    firebase_credentials = settings.FIREBASE_CREDENTIALS_DATA
    certificate = credentials.Certificate(
        firebase_credentials.model_dump()
    )
    return firebase_admin.initialize_app(certificate)


s3_client = get_s3_client()
