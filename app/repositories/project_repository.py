from . import BaseRepository
from app.models import Project, Task, Group

class ProjectRepository(BaseRepository):

    def save(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project_by_group_id(self, group_id: int, project_id: int) -> Project | None:
        ...

    def get_project_tasks(self, project_id: int) -> list[Task] | None:
        ...

    def remove(self, project: Project) -> None:
        ...