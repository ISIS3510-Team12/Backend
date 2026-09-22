from app.core.consts import (
    BASED_ON_FALLBACK,
    BASED_ON_HISTORY,
    DEFAULT_TASK_DURATION_MINUTES,
    EventType,
    SECONDS_PER_MINUTE,
)
from app.models import Task, User
from app.repositories.task_event_repository import TaskEventRepository
from app.repositories.task_repository import TaskRepository


class TaskInsightsService:
    def __init__(
        self,
        task_repository: TaskRepository,
        task_event_repository: TaskEventRepository,
    ):
        self.task_repository = task_repository
        self.task_event_repository = task_event_repository

    def get_task(self, task_id: int) -> Task | None:
        return self.task_repository.get_by_id(task_id)

    def user_can_access_task(self, task: Task, user: User) -> bool:
        """
        A user can access a task when they own it or belong to the task's group.
        """
        if task.user_id == user.user_id:
            return True

        project = task.project
        if project is None:
            return False

        for group in user.groups:
            if group.id == project.group_id:
                return True

        return False

    def estimate_task_duration(self, task: Task, user: User) -> dict:
        """
        A smart feature, where it suggests how long a task will take based on how long
        similar completed tasks of the same user actually took in the past.
        """
        similar_tasks = self.task_repository.get_completed_tasks_by_type(
            user.user_id,
            task.task_type,
            task.id,
        )

        durations: list[int] = []
        for similar_task in similar_tasks:
            duration = self.actual_duration_minutes(similar_task)
            if duration is None:
                continue
            durations.append(duration)

        if len(durations) == 0:
            return {
                "suggested_duration_minutes": DEFAULT_TASK_DURATION_MINUTES,
                "current_estimate_minutes": DEFAULT_TASK_DURATION_MINUTES,
                "sample_size": 0,
                "based_on": BASED_ON_FALLBACK,
            }

        total = 0
        for duration in durations:
            total = total + duration

        average = round(total / len(durations))

        return {
            "suggested_duration_minutes": average,
            "current_estimate_minutes": DEFAULT_TASK_DURATION_MINUTES,
            "sample_size": len(durations),
            "based_on": BASED_ON_HISTORY,
        }

    def actual_duration_minutes(self, task: Task) -> int | None:
        """
        Measures how long a task took by pairing its started and completed events.
        """
        events = self.task_event_repository.get_events_for_task(task.id)

        started_at = None
        completed_at = None

        for event in events:
            if event.event_type == EventType.STARTED:
                if started_at is None:
                    started_at = event.occurred_at
                elif event.occurred_at < started_at:
                    started_at = event.occurred_at
            elif event.event_type == EventType.COMPLETED:
                if completed_at is None:
                    completed_at = event.occurred_at
                elif event.occurred_at > completed_at:
                    completed_at = event.occurred_at

        if started_at is None:
            return None

        if completed_at is None:
            return None

        if completed_at < started_at:
            return None

        delta = completed_at - started_at
        return round(delta.total_seconds() / SECONDS_PER_MINUTE)
