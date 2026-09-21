from . import BaseRepository
from app.models import Project, Task, Group

class ProjectRepository(BaseRepository):

    def save(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    