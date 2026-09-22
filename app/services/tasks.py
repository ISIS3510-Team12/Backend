from sqlmodel import Session, select

from app.core.consts import (
    BASED_ON_FALLBACK,
    BASED_ON_HISTORY,
    DEFAULT_TASK_DURATION_MINUTES,
    EventType,
    SECONDS_PER_MINUTE,
    STATUS_COMPLETED,
)
from app.models import Project, Task, User, UserGroup
from app.repositories.task_event_repository import TaskEventRepository


def user_can_access_task(db: Session, task: Task, user: User) -> bool:
    """
    A user can access a task when they own it or belong to the task's group.
    """
    if task.user_id == user.user_id:
        return True

    project = db.get(Project, task.project_id)
    if project is None:
        return False

    membership = db.get(UserGroup, (user.user_id, project.group_id))
    if membership is None:
        return False

    return True


def estimate_task_duration(db: Session, task: Task, user: User) -> dict:
    """
    A smart feature, where it suggests how long a task will take based on how long
    similar completed tasks of the same user actually took in the past.
    """
    similar_tasks = db.exec(
        select(Task).where(
            Task.user_id == user.user_id,
            Task.id != task.id,
            Task.status == STATUS_COMPLETED,
            Task.task_type == task.task_type,
        )
    ).all()

    durations: list[int] = []
    for similar_task in similar_tasks:
        duration = actual_duration_minutes(db, similar_task)
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


def actual_duration_minutes(db: Session, task: Task) -> int | None:
    """
    Measures how long a task took by pairing its started and completed events.
    """
    event_repository = TaskEventRepository(db)
    events = event_repository.get_events_for_task(task.id)

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
