import uuid
from datetime import datetime, timezone

from botocore.exceptions import ClientError
from sqlalchemy.exc import IntegrityError
from types_boto3_s3.client import S3Client

from app.core.config import settings
from app.exceptions import (
    ProjectNotFoundException,
    ProjectPhotoDeleteForbiddenException,
    ProjectPhotoNotFoundException,
)
from app.models import ProjectPhoto, User
from app.repositories.project_photo_repository import ProjectPhotoRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas import ProjectPhotoResponse
from app.services.mappers import to_project_photo_response

StoredObject = tuple[str, str]
PhotoContent = tuple[bytes, str]


class ProjectPhotoService:
    def __init__(
        self,
        repository: ProjectPhotoRepository,
        project_repository: ProjectRepository,
        s3_client: S3Client,
    ):
        self.repository = repository
        self.project_repository = project_repository
        self.s3_client = s3_client

    def get_photos(self, project_id: int, user_id: str) -> list[ProjectPhotoResponse]:
        self._check_access(project_id, user_id)
        return [
            to_project_photo_response(photo, uploader)
            for photo, uploader in self.repository.get_by_project(project_id)
        ]

    def upload_photo(
        self,
        project_id: int,
        user: User,
        client_upload_id: str,
        caption: str | None,
        photo: PhotoContent,
        thumbnail: PhotoContent | None,
    ) -> tuple[ProjectPhotoResponse, bool]:
        self._check_access(project_id, user.user_id)
        existing = self.repository.get_by_client_upload_id(
            project_id, user.user_id, client_upload_id
        )
        if existing is not None:
            return to_project_photo_response(existing, user), False

        user_id = user.user_id
        folder = f"projects/{project_id}/{uuid.uuid4().hex}"
        stored: list[StoredObject] = []
        try:
            key = self._store(folder, "photo", photo, stored)
            thumbnail_key = (
                None
                if thumbnail is None
                else self._store(folder, "thumbnail", thumbnail, stored)
            )
            created = self.repository.create(
                ProjectPhoto(
                    project_id=project_id,
                    uploader_id=user_id,
                    client_upload_id=client_upload_id,
                    caption=caption,
                    bucket=settings.S3_BUCKET,
                    key=key,
                    thumbnail_key=thumbnail_key,
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
        except IntegrityError:
            self.repository.rollback()
            self.remove_stored_objects(stored)
            duplicate = self.repository.get_by_client_upload_id(
                project_id, user_id, client_upload_id
            )
            if duplicate is None:
                raise
            return to_project_photo_response(duplicate, user), False
        except Exception:
            self.remove_stored_objects(stored)
            raise
        return to_project_photo_response(created, user), True

    def get_content(
        self, project_id: int, photo_id: int, user_id: str, thumbnail: bool
    ) -> tuple[object, str]:
        photo = self._get_photo(project_id, photo_id, user_id)
        key = photo.thumbnail_key if thumbnail and photo.thumbnail_key else photo.key
        try:
            response = self.s3_client.get_object(Bucket=photo.bucket, Key=key)
        except ClientError:
            raise ProjectPhotoNotFoundException(photo_id)
        return response["Body"], response.get("ContentType", "image/jpeg")

    def delete_photo(self, project_id: int, photo_id: int, user_id: str) -> None:
        photo = self._get_photo(project_id, photo_id, user_id)
        if photo.uploader_id != user_id:
            raise ProjectPhotoDeleteForbiddenException()
        objects = self._objects_of(photo)
        self.repository.delete(photo)
        self.remove_stored_objects(objects)

    def get_stored_objects_of_project(self, project_id: int) -> list[StoredObject]:
        return [
            stored
            for photo, _ in self.repository.get_by_project(project_id)
            for stored in self._objects_of(photo)
        ]

    def get_stored_objects_of_group(self, group_id: int) -> list[StoredObject]:
        return [
            stored
            for photo in self.repository.get_by_group(group_id)
            for stored in self._objects_of(photo)
        ]

    def remove_stored_objects(self, objects: list[StoredObject]) -> None:
        for bucket, key in objects:
            try:
                self.s3_client.delete_object(Bucket=bucket, Key=key)
            except ClientError:
                pass

    def _check_access(self, project_id: int, user_id: str) -> None:
        if self.project_repository.get_project_by_id(project_id, user_id) is None:
            raise ProjectNotFoundException(project_id)

    def _get_photo(self, project_id: int, photo_id: int, user_id: str) -> ProjectPhoto:
        self._check_access(project_id, user_id)
        photo = self.repository.get_by_id(project_id, photo_id)
        if photo is None:
            raise ProjectPhotoNotFoundException(photo_id)
        return photo

    def _store(
        self,
        folder: str,
        name: str,
        content: PhotoContent,
        stored: list[StoredObject],
    ) -> str:
        body, content_type = content
        key = f"{folder}/{name}.{content_type.split('/')[-1]}"
        self.s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=body,
            ContentType=content_type,
        )
        stored.append((settings.S3_BUCKET, key))
        return key

    def _objects_of(self, photo: ProjectPhoto) -> list[StoredObject]:
        keys = [photo.key, photo.thumbnail_key]
        return [(photo.bucket, key) for key in keys if key is not None]
