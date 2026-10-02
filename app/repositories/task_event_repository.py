from sqlalchemy import and_, func, or_
from sqlmodel import select

from . import BaseRepository
from app.core.consts import TaskEventType, TaskStatus
from app.models import Group, Task, TaskEvent, UserGroup

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

    def get_project_first_event_at(self, project_id: int):
        """Occurred_at of the earliest event among a project's tasks."""
        statement = (
            select(func.min(TaskEvent.occurred_at))
            .join(Task, Task.id == TaskEvent.task_id)
            .where(Task.project_id == project_id)
        )
        return self.db.exec(statement).first()
    
    def get_notifications_by_user_groups(self, user_id: str) -> list:
        """
        Task events (excluding the views) for tasks in the user's groups.
        """
        statement = (
            select(TaskEvent, Task, Group)
            .join(Task, Task.id == TaskEvent.task_id)
            .join(Group, Group.id == Task.group_id)
            .join(UserGroup, UserGroup.group_id == Task.group_id)
            .where(UserGroup.user_id == user_id)
            .where(TaskEvent.event_type != TaskEventType.VIEWED)
            .where(
                or_(
                    TaskEvent.event_type == TaskEventType.CREATED,
                    TaskEvent.event_type == TaskEventType.UPDATED,
                    TaskEvent.event_type == TaskEventType.DELETED,
                    and_(
                        TaskEvent.event_type == TaskEventType.STATUS_CHANGED,
                        TaskEvent.task_status == TaskStatus.COMPLETED,
                    ),
                )
            )
            .order_by(TaskEvent.occurred_at.desc())
        )
        return list(self.db.exec(statement).all())
