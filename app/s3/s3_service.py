from __future__ import annotations
from typing import final
from botocore.exceptions import ClientError
from dataclasses import dataclass
from app.core.dependencies import s3_client, s3_resource
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_boto3_s3.service_resource import BucketObjectsCollection

@dataclass
class S3Object:
    key: str
    last_modified: str
    size: int
    storage_class: str


@final
class S3Service:

    def create_bucket(self, bucket_name: str):
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        except Exception as e:
            print(f"Error creating bucket '{bucket_name}': {e}")

    def get_bucket_files(self, bucket_name: str):
        try:
            bucket = s3_resource.Bucket(bucket_name)
            if self._bucket_exists(bucket_name):
                objects: BucketObjectsCollection = bucket.objects.all()
                objects_info = []

                for obj in objects:
                    objects_info.append(
                        S3Object(
                            key=obj.key,
                            last_modified=obj.last_modified.isoformat(),
                            size=obj.size,
                            storage_class=obj.storage_class,
                        )
                    )

                return {
                    "name": bucket.name,
                    "creation_date": bucket.creation_date,
                    "objects": objects_info,
                }

            else:
                return None
        except Exception as e:
            print(f"Error getting bucket '{bucket_name}': {e}")
            return None

    def download_file(self, bucket_name: str, object_key: str):
        try:
            if not self._check_file_exists_in_bucket(bucket_name, object_key):
                print(
                    f"File '{object_key}' does not exist in bucket '{bucket_name}'.")
                return None
            response = s3_client.get_object(
                Bucket=bucket_name, Key=object_key)
            body = response["Body"]
            return body
        except Exception as e:
            print(
                f"Error downloading file '{object_key}' from bucket '{bucket_name}': {e}")

    def _check_file_exists_in_bucket(
        self,
        bucket_name: str,
        object_key: str,
    ) -> bool:
        try:
            if not self._bucket_exists(bucket_name):
                return False
            s3_client.head_object(
                Bucket=bucket_name,
                Key=object_key,
            )
            return True
        except ClientError as e:
            metadata = e.response.get("ResponseMetadata", {})
            status_code = metadata.get("HTTPStatusCode")
            if status_code == 404:
                return False
            raise

    def _bucket_exists(self, bucket_name: str) -> bool:
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            return True
        except Exception as e:
            print(f"Error checking bucket '{bucket_name}': {e}")
            return False


s3_service = S3Service()
