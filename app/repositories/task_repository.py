from . import BaseRepository
from app.models import Task

class TaskRepository(BaseRepository):

    def save(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    