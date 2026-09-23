from . import BaseRepository
from app.models import Project, Task, Group

class ProjectRepository(BaseRepository):
    def get_project_by_id(self, project_id: int, user_id: int) -> Project | None:
        # TODO: check if user can access this project
        return self.db.get(Project, project_id)