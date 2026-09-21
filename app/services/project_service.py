from app.models import Project, Task
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, project: Project) -> Project:
        ...

    def get_project_by_group_id(self, group_id: int, project_id: int) -> Project:
        ...

    def get_project_tasks(self, project_id: int) -> list[Task]:
        ...

    def remove_project(self, project: Project) -> None:
        ...



    


    
    

    