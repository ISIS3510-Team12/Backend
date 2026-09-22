from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError
from app.core.dependencies.external import get_s3_client

router = APIRouter(
    prefix="/s3",
)

@router.get("/buckets/{bucket_name}")
def get_bucket(bucket_name: str, s3_client=Depends(get_s3_client)):
    try:
        # Check if the bucket exists by calling head_bucket
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        return {"message": f"Bucket '{bucket_name}' not found."}

    response = s3_client.list_objects_v2(Bucket=bucket_name)

    objects_info = []

    # S3 returns the raw list of files inside response["Contents"].
    # We loop over it to pick only the fields the API needs
    if "Contents" in response:
        for item in response["Contents"]:
            last_modified = item["LastModified"]
            last_modified_text = last_modified.isoformat()

            storage_class = ""
            if "StorageClass" in item:
                storage_class = item["StorageClass"]

            file_info = {}
            file_info["key"] = item["Key"]
            file_info["last_modified"] = last_modified_text
            file_info["size"] = item["Size"]
            file_info["storage_class"] = storage_class

            objects_info.append(file_info)

    bucket_info = {}
    bucket_info["name"] = bucket_name
    bucket_info["objects"] = objects_info

    return {"bucket": bucket_info}


@router.put("/buckets/{bucket_name}")
def create_bucket(bucket_name: str, s3_client=Depends(get_s3_client)):
    try:
        s3_client.create_bucket(Bucket=bucket_name)
    except ClientError:
        return {"message": f"Bucket '{bucket_name}' could not be created."}

    return {"message": f"Bucket '{bucket_name}' created successfully."}


@router.get("/buckets/{bucket_name}/download/{object_key}")
def download_file(
    bucket_name: str, object_key: str, s3_client=Depends(get_s3_client)
):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    except ClientError:
        return {
            "message": f"File '{object_key}' not found in bucket '{bucket_name}'."
        }

    body = response["Body"]

    parts = object_key.split("/")
    filename = parts[-1]

    return StreamingResponse(
        body,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
