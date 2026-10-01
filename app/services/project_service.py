from app.models import Project
from app.repositories.project_repository import ProjectRepository
from app.exceptions import GroupNotFoundException, ProjectNotFoundException
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, user_id: str, data: ProjectCreate) -> Project:
        if not self.repository.user_belongs_to_group(
            data.group_id,
            user_id
        ):
            raise GroupNotFoundException(data.group_id)

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
            raise GroupNotFoundException(group_id)

        return self.repository.get_projects_by_group(group_id, user_id)
    
    def update_project(self, project_id: int, user_id: str, data: ProjectUpdate) -> Project | None:
        project = self.repository.get_project_by_id(
            project_id,
            user_id
        )

        if project is None:
            raise ProjectNotFoundException(project_id)

        changes = data.model_dump(exclude_unset=True)
        new_group_id = changes.get("group_id")
        if new_group_id is not None and new_group_id != project.group_id:
            if not self.repository.user_belongs_to_group(new_group_id, user_id):
                raise GroupNotFoundException(new_group_id)

        updated = self.repository.update_project(project, changes)
        self.repository.sync_task_groups(updated)
        return updated
    
    def delete_project(self, project_id: int, user_id: str) -> bool:
        project = self.repository.get_project_by_id(
            project_id,
            user_id
        )

        if project is None:
            raise ProjectNotFoundException(project_id)

        self.repository.delete_project(project)

        return True
        

    