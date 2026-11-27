from sqlmodel import select

from . import BaseRepository
from app.models import Project, ProjectPhoto, User


class ProjectPhotoRepository(BaseRepository):

    def get_by_project(self, project_id: int) -> list[tuple[ProjectPhoto, User]]:
        statement = (
            select(ProjectPhoto, User)
            .join(User, User.user_id == ProjectPhoto.uploader_id)
            .where(ProjectPhoto.project_id == project_id)
            .order_by(ProjectPhoto.created_at.desc(), ProjectPhoto.id.desc())
        )
        return list(self.db.exec(statement).all())

    def get_by_id(self, project_id: int, photo_id: int) -> ProjectPhoto | None:
        statement = select(ProjectPhoto).where(
            ProjectPhoto.id == photo_id,
            ProjectPhoto.project_id == project_id,
        )
        return self.db.exec(statement).first()

    def get_by_client_upload_id(
        self, project_id: int, uploader_id: str, client_upload_id: str
    ) -> ProjectPhoto | None:
        statement = select(ProjectPhoto).where(
            ProjectPhoto.project_id == project_id,
            ProjectPhoto.uploader_id == uploader_id,
            ProjectPhoto.client_upload_id == client_upload_id,
        )
        return self.db.exec(statement).first()

    def get_by_group(self, group_id: int) -> list[ProjectPhoto]:
        statement = (
            select(ProjectPhoto)
            .join(Project, Project.id == ProjectPhoto.project_id)
            .where(Project.group_id == group_id)
        )
        return list(self.db.exec(statement).all())

    def create(self, photo: ProjectPhoto) -> ProjectPhoto:
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)

        return photo

    def rollback(self) -> None:
        self.db.rollback()

    def delete(self, photo: ProjectPhoto) -> None:
        self.db.delete(photo)
        self.db.commit()
