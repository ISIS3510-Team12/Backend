from sqlmodel import select

from . import BaseRepository
from app.models import Project, Task, Group

class ProjectRepository(BaseRepository):
    def get_project_by_id(self, project_id: int, user_id: int) -> Project | None:
        # TODO: check if user can access this project
        return self.db.get(Project, project_id)

    def create_project(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project

    def get_projects_by_group_id(self, group_id: int) -> list[Project]:
        statement = select(Project).where(Project.group_id == group_id)
        results = self.db.exec(statement).all()

        return list(results)

    def get_tasks_by_project_id(self,project_id: int) -> list[Task]:
        statement = select(Task).where(Task.project_id == project_id)
        results = self.db.exec(statement).all()
        
        return list(results)
