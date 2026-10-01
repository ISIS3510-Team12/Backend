from sqlmodel import select

from . import BaseRepository
from app.models import Project, Task, UserGroup


class ProjectRepository(BaseRepository):

    def user_belongs_to_group(self, group_id: int, user_id: str) -> bool:
        statement = select(UserGroup).where(
            UserGroup.group_id == group_id,
            UserGroup.user_id == user_id
        )
        return self.db.exec(statement).first() is not None

    def get_project_by_id(self, project_id: int, user_id: str) -> Project | None:
        statement = (
            select(Project)
            .join(
                UserGroup,
                UserGroup.group_id == Project.group_id
            )
            .where(
                Project.id == project_id,
                UserGroup.user_id == user_id
            )
        )
        return self.db.exec(statement).first()

    def create_project(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def get_projects_by_group_id(self, group_id: int) -> list[Project]:
        statement = select(Project).where(
            Project.group_id == group_id
        )
        results = self.db.exec(statement).all()

        return list(results)

    def get_projects_by_group(self, group_id: int, user_id: str) -> list[Project]:
        statement = (
            select(Project)
            .join(
                UserGroup,
                UserGroup.group_id == Project.group_id
            )
            .where(
                Project.group_id == group_id,
                UserGroup.user_id == user_id
            )
        )
        results = self.db.exec(statement).all()

        return list(results)

    def get_tasks_by_project_id(self, project_id: int) -> list[Task]:
        statement = select(Task).where(
            Task.project_id == project_id
        )
        results = self.db.exec(statement).all()

        return list(results)

    def update_project(self, project: Project, data: dict) -> Project:
        for field, value in data.items():
            setattr(project, field, value)

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def delete_project(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()