from app.models import Project
from app.repositories.project_repository import ProjectRepository
from app.exceptions import ProjectNotFoundException
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, user_id: str, data: ProjectCreate) -> Project:
        if not self.repository.user_belongs_to_group(
            data.group_id,
            user_id
        ):
            raise Exception("User does not belong to this group")

        project = Project(
            name=data.name,
            description=data.description,
            deadline=data.deadline,
            group_id=data.group_id
        )
        return self.repository.create_project(project)

    def get_project_by_user(self, project_id: int, user_id: str) -> Project:
        project = self.repository.get_project_by_id(
            project_id,
            user_id
        )
        if project is None:
            raise ProjectNotFoundException(project_id)

        return project

    def get_projects_by_group(self, group_id: int, user_id: str) -> list[Project]:
        if not self.repository.user_belongs_to_group(
            group_id,
            user_id
        ):
            raise Exception("User does not belong to this group")

        return self.repository.get_projects_by_group(group_id, user_id)
    
    def update_project(self, project_id: int, user_id: str, data: ProjectUpdate) -> Project | None:
        project = self.repository.get_project_by_id(
            project_id,
            user_id
        )

        if project is None:
            raise ProjectNotFoundException(project_id)

        return self.repository.update_project(
            project,
            data.model_dump(exclude_unset=True)
        )
    
    def delete_project(self, project_id: int, user_id: str) -> bool:
        project = self.repository.get_project_by_id(
            project_id,
            user_id
        )

        if project is None:
            raise ProjectNotFoundException(project_id)

        self.repository.delete_project(project)

        return True
        

    