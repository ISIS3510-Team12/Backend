from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.s3.s3_service import s3_service
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/s3",
)

@router.get("/buckets/{bucket_name}")
def get_bucket(bucket_name: str):
    bucket_info = s3_service.get_bucket_files(bucket_name)
    if bucket_info:
        return {"bucket": bucket_info}
    else:
        return {"message": f"Bucket '{bucket_name}' not found."}

@router.put("/buckets/{bucket_name}")
def create_bucket(bucket_name: str):
    s3_service.create_bucket(bucket_name)
    return {"message": f"Bucket '{bucket_name}' created successfully."}

@router.get("/buckets/{bucket_name}/download/{object_key}")
def download_file(bucket_name: str, object_key: str):

    file = s3_service.download_file(bucket_name, object_key)
    if file:
        return StreamingResponse(file, media_type="application/octet-stream", headers={
            "Content-Disposition": (
                f'attachment; filename="{object_key.split("/")[-1]}"'
            )
        })
    else:
        return {"message": f"File '{object_key}' not found in bucket '{bucket_name}'."}
