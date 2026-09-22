from app.models import Project, Task
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, project: Project) -> Project:
        ...




    


    
    

    