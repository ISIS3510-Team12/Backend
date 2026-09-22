from __future__ import annotations
from typing import TYPE_CHECKING
from contextlib import asynccontextmanager
from fastapi import FastAPI
from botocore.exceptions import ClientError
from app.core.dependencies.external import initialize_firebase_app, s3_client
from app.core.logger import get_logger

if TYPE_CHECKING:
    from types_boto3_s3.client import S3Client

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_bucket(
        s3_client=s3_client,
        bucket_name="files",
    )
    initialize_firebase_app()
    yield


def setup_bucket(s3_client: S3Client, bucket_name: str):
    """
    Create the initial S3 bucket (files) if it doesn't exist.
    """
    bucket_exists = True

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' already exists.")
    except ClientError:
        bucket_exists = False

    if not bucket_exists:
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully.")

            s3_client.put_object(
                Bucket=bucket_name,
                Key="attachments/blob.txt",
                Body=b"Hello, World!",
                ContentType="text/plain",
            )

            logger.info(f"Test blob created in bucket '{bucket_name}'.")

        except ClientError as e:
            logger.error(
                f"Could not initialize bucket '{bucket_name}': {str(e)}"
            )

            return {
                "message": f"Bucket '{bucket_name}' could not be initialized.",
                "error": str(e),
            }

    logger.info(f"Bucket '{bucket_name}' is ready for use.")
