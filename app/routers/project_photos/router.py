from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.consts import (
    ALLOWED_PHOTO_CONTENT_TYPES,
    MAX_CLIENT_UPLOAD_ID_LENGTH,
    MAX_PHOTO_CAPTION_LENGTH,
    MAX_PHOTO_SIZE_BYTES,
    MAX_THUMBNAIL_SIZE_BYTES,
    PHOTO_CACHE_MAX_AGE_SECONDS,
)
from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import ProjectPhotoServiceDep
from app.schemas import ProjectPhotoResponse

router = APIRouter(
    prefix="/projects/{project_id}/photos",
    tags=["project photos"]
)


def read_photo(file: UploadFile, max_size: int) -> tuple[bytes, str]:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_PHOTO_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The photo must be a JPEG, PNG, WebP or HEIC image.",
        )
    content = file.file.read(max_size + 1)
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="The photo exceeds the maximum allowed size.",
        )
    return content, content_type


@router.get("", response_model=list[ProjectPhotoResponse], status_code=status.HTTP_200_OK)
def get_project_photos(project_id: int, current_user: CurrentUser, service: ProjectPhotoServiceDep):
    return service.get_photos(project_id, current_user.user_id)


@router.post("", response_model=ProjectPhotoResponse, status_code=status.HTTP_201_CREATED)
def upload_project_photo(
    project_id: int,
    response: Response,
    current_user: CurrentUser,
    service: ProjectPhotoServiceDep,
    file: UploadFile = File(...),
    thumbnail: UploadFile | None = File(None),
    client_upload_id: str = Form(..., min_length=1, max_length=MAX_CLIENT_UPLOAD_ID_LENGTH),
    caption: str | None = Form(None, max_length=MAX_PHOTO_CAPTION_LENGTH),
):
    photo, created = service.upload_photo(
        project_id,
        current_user,
        client_upload_id,
        caption,
        read_photo(file, MAX_PHOTO_SIZE_BYTES),
        None if thumbnail is None else read_photo(thumbnail, MAX_THUMBNAIL_SIZE_BYTES),
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return photo


@router.get("/{photo_id}", status_code=status.HTTP_200_OK)
def get_project_photo(
    project_id: int,
    photo_id: int,
    current_user: CurrentUser,
    service: ProjectPhotoServiceDep,
    variant: Literal["full", "thumb"] = Query("full"),
):
    body, content_type = service.get_content(
        project_id, photo_id, current_user.user_id, variant == "thumb"
    )
    return StreamingResponse(
        body,
        media_type=content_type,
        headers={"Cache-Control": f"private, max-age={PHOTO_CACHE_MAX_AGE_SECONDS}"},
    )


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_photo(
    project_id: int,
    photo_id: int,
    current_user: CurrentUser,
    service: ProjectPhotoServiceDep,
):
    service.delete_photo(project_id, photo_id, current_user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
