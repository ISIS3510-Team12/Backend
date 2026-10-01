from __future__ import annotations
import boto3
import firebase_admin
import os
from botocore.config import Config
from functools import lru_cache
from firebase_admin import App, credentials
from app.core.config import settings
from typing import Annotated
from fastapi import Depends
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
        region_name=settings.S3_REGION or "us-east-1",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


@lru_cache
def initialize_firebase_app() -> App:
    emulator_host = settings.FIREBASE_AUTH_EMULATOR_HOST

    if settings.ENV == "dev" and emulator_host:
        project_id = settings.FIREBASE_PROJECT_ID or settings.FIREBASE_CREDENTIALS_DATA.project_id
        if not project_id:
            raise ValueError(
                "FIREBASE_PROJECT_ID must be set to use the Firebase Auth emulator."
            )

        # The Admin SDK reads FIREBASE_AUTH_EMULATOR_HOST from the process environment at call time.
        os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = emulator_host
        return firebase_admin.initialize_app(options={"projectId": project_id})

    firebase_credentials = settings.FIREBASE_CREDENTIALS_DATA
    data = firebase_credentials.model_dump()
    data["private_key"] = data["private_key"].replace("\\n", "\n")
    certificate = credentials.Certificate(data)
    return firebase_admin.initialize_app(certificate)


S3ClientDep = Annotated[
    S3Client,
    Depends(get_s3_client),
]

s3_client = get_s3_client()
