from app.models import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas import ProjectCreate, ProjectResponse
from app.services.mappers import to_project_response


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, user_id: str, data: ProjectCreate) -> ProjectResponse:
        project = Project(
            name=data.name,
            description=data.description,
            deadline=data.deadline,
            group_id=data.group_id,
        )
        return to_project_response(self.repository.create_project(project))

    def get_projects_by_group(self, group_id: int, user_id: str) -> list[ProjectResponse]:
        projects = self.repository.get_projects_by_group_id(group_id)
        responses: list[ProjectResponse] = []
        for project in projects:
            responses.append(to_project_response(project))
        return responses
