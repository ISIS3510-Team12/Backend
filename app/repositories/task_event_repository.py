from sqlalchemy import and_, or_
from sqlmodel import select

from . import BaseRepository
from app.core.consts import TaskEventType, TaskStatus
from app.models import Group, Project, Task, TaskEvent, UserGroup

class TaskEventRepository(BaseRepository):
    def register_task_event(self, task_event: TaskEvent) -> TaskEvent:
            self.db.add(task_event)
            self.db.commit()
            self.db.refresh(task_event)
            return task_event
        
    def get_task_events_by_task_id(self, task_id: int) -> list[TaskEvent]:
        statement = select(TaskEvent).where(TaskEvent.task_id == task_id)
        results = self.db.exec(statement).all()
        return list(results)
    
    def get_task_events_by_user_id(self, user_id: int) -> list[TaskEvent]:
        statement = select(TaskEvent).where(TaskEvent.author_id == user_id)
        results = self.db.exec(statement).all()
        return list(results)