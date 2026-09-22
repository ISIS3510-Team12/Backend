from . import BaseRepository
from app.models import Project, Task, Group

class ProjectRepository(BaseRepository):
    def get_project_by_id(self, project_id: int) -> Project | None:
        return self.db.get(Project, project_id)