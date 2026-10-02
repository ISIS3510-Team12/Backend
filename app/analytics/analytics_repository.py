from datetime import datetime, timedelta

from sqlalchemy import func, literal, union_all
from sqlmodel import select

from app.core.consts import TaskEventType, TaskStatus
from app.repositories import BaseRepository
from app.models import (
    Group,
    Project,
    ScreenLoadEvent,
    Task,
    TaskAssignee,
    TaskEvent,
)


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
                Task.group_id.label("group_id"),
                Task.user_id.label("owner_id"),
                first_viewed.c.first_viewed_at,
                completed.c.completed_at,
            )
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

    def get_upcoming_tasks_due(self, now: datetime, days: int) -> list:
        """
        One row per (user, task) for every pending task with a deadline in the
        next `days` days. A task counts for its owner and for each assignee.
        This is the answer to the Business Question:
        "Which upcoming tasks does the user have due in the next week?"
        """
        owners = select(
            Task.id.label("task_id"),
            Task.user_id.label("user_id"),
            literal("owner").label("user_role"),
        )

        assignees = (
            select(
                TaskAssignee.task_id.label("task_id"),
                TaskAssignee.user_id.label("user_id"),
                literal("assignee").label("user_role"),
            )
            .join(Task, Task.id == TaskAssignee.task_id)
            .where(TaskAssignee.user_id != Task.user_id)
        )

        participants = union_all(owners, assignees).subquery()

        statement = (
            select(
                participants.c.user_id,
                participants.c.user_role,
                Task.id.label("task_id"),
                Task.title.label("task_title"),
                Task.task_type.label("task_type"),
                Task.status.label("task_status"),
                Task.is_priority.label("is_priority"),
                Task.needs_help.label("needs_help"),
                Task.deadline.label("deadline"),
                Task.group_id.label("group_id"),
                Group.name.label("group_name"),
                Task.project_id.label("project_id"),
                Project.name.label("project_name"),
            )
            .select_from(Task)
            .join(participants, participants.c.task_id == Task.id)
            .join(Group, Group.id == Task.group_id)
            .outerjoin(Project, Project.id == Task.project_id)
            .where(
                Task.deadline.is_not(None),
                Task.status != TaskStatus.COMPLETED,
                Task.deadline >= now,
                Task.deadline <= now + timedelta(days=days),
            )
            .order_by(participants.c.user_id, Task.deadline, Task.id)
        )

        return list(self.db.exec(statement).all())

    def get_task_completion_deadlines(self) -> list:
        """
        One row per task that has a deadline and a completion event.
        This is for the answer to the Business Question:
        "On average, how much time before deadline do students complete their tasks?"
        """
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
                Task.user_id.label("owner_id"),
                completed.c.completed_at,
                Task.deadline.label("deadline"),
            )
            .join(completed, completed.c.task_id == Task.id)
            .where(Task.deadline.is_not(None))
            .order_by(Task.user_id, Task.deadline, Task.id)
        )

        return list(self.db.exec(statement).all())

    def get_frecuently_task_types(self) -> list:
        """
        One row per task type with the count of tasks of that type.
        This is for the answer to the Business Question:
        "Which types of tasks are created most frequently by students?"
        """
        statement = (
            select(
                Task.task_type.label("task_type"),
                func.count(Task.id).label("task_count"),
            )
            .group_by(Task.task_type)
            .order_by(func.count(Task.id).desc())
        )

        rows = self.db.exec(statement).all()

        result = []

        for task_type, task_count in rows:
            result.append({
                "task_type": task_type,
                "task_count": task_count,
            })

        return result
