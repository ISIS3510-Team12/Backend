from sqlalchemy import func
from sqlmodel import select

from app.core.consts import TaskEventType, TaskStatus
from app.repositories import BaseRepository
from app.models import Project, Task, TaskEvent, ScreenLoadEvent


class AnalyticsRepository(BaseRepository):
    def get_task_completion_times(self) -> list:
        """
        One row per task that has both a first view and a completion event.
        This is the answer to the Business Question:
        "How long does it take users to complete a task after first opening it?"
        """
        first_viewed = (
            select(
                TaskEvent.task_id.label("task_id"),
                func.min(TaskEvent.occurred_at).label("first_viewed_at"),
            )
            .where(TaskEvent.event_type == TaskEventType.VIEWED)
            .group_by(TaskEvent.task_id)
            .subquery()
        )

        completed = (
            select(
                TaskEvent.task_id.label("task_id"),
                func.min(TaskEvent.occurred_at).label("completed_at"),
            )
            .where(TaskEvent.event_type == TaskEventType.STATUS_CHANGED)
            .where(TaskEvent.task_status == TaskStatus.COMPLETED)
            .group_by(TaskEvent.task_id)
            .subquery()
        )

        statement = (
            select(
                Task.id.label("task_id"),
                Task.title.label("task_title"),
                Task.project_id.label("project_id"),
                Project.group_id.label("group_id"),
                Task.user_id.label("owner_id"),
                first_viewed.c.first_viewed_at,
                completed.c.completed_at,
            )
            .join(Project, Project.id == Task.project_id)
            .join(first_viewed, first_viewed.c.task_id == Task.id)
            .join(completed, completed.c.task_id == Task.id)
            .where(completed.c.completed_at >= first_viewed.c.first_viewed_at)
            .order_by(Task.id)
        )

        return list(self.db.exec(statement).all())

    def get_screen_load_times(self) -> list:
        statement = (
            select(
                ScreenLoadEvent.screen,
                func.avg(
                    ScreenLoadEvent.load_time_ms
                ).label("average_load_time_ms"),
            )
            .group_by(ScreenLoadEvent.screen)
            .order_by(ScreenLoadEvent.screen)
        )

        return list(self.db.exec(statement).all())