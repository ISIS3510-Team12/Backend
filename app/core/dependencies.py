from __future__ import annotations
from app.core.config import settings
import boto3
from functools import lru_cache
from typing import TYPE_CHECKING

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

s3_client = get_s3_client()
s3_resource = get_s3_resource()
