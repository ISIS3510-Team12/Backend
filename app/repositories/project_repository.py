from . import BaseRepository
from app.models import Project, Task, Group

class ProjectRepository(BaseRepository):

    def save(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project_by_group_id(self, group_id: str, project_id: str) -> Project | None:
        project = self.db.get(Project, project_id)
        if project and project.group_id == group_id:
            return project
        return None

    def get_project_tasks(self, project_id: str) -> list[Task] | None:
        project = self.db.get(Project, project_id)
        if project:
            return project.tasks
        return None

    def get_project_group(self, project_id: str) -> Group | None:
        project = self.db.get(Project, project_id)
        if project:
            return project.group
        return None

    def remove(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()

    