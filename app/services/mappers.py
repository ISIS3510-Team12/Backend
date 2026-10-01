from datetime import datetime

from app.core.consts import AttachmentKind
from app.models import Group, Project, Reminder, Task, TimeBlock, User
from app.schemas import (
    GroupResponse,
    ProjectResponse,
    ReminderResponse,
    TaskResponse,
    TaskSummary,
    TimeBlockResponse,
    UserResponse,
)


def pluralized(value: int, singular: str, plural: str) -> str:
    """
    Return a string with the value and the singular or plural form of a word.
    """
    if value == 1:
        return f"{value} {singular}"
    return f"{value} {plural}"


def format_reminder_label(
    deadline: datetime | None,
    scheduled_at: datetime | None,
) -> str | None:
    """
    Humanise a reminder's offset from the task deadline (For example "1 day before").
    """
    if deadline is None or scheduled_at is None:
        return None

    offset = int((deadline - scheduled_at).total_seconds() // 60)
    if offset == 0:
        return "At deadline"

    direction = "before"
    if offset < 0:
        direction = "after"
        offset = -offset

    days, remainder = divmod(offset, 60 * 24)
    hours, minutes = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(pluralized(days, "day", "days"))
    if hours:
        parts.append(pluralized(hours, "hour", "hours"))
    if minutes:
        parts.append(pluralized(minutes, "minute", "minutes"))

    return f"{' '.join(parts[:2])} {direction}" # Limit to two largest units ("1 day 3 hours before")


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def to_reminder_response(
    reminder: Reminder,
    deadline: datetime | None,
) -> ReminderResponse:
    return ReminderResponse(
        id=reminder.id,
        enabled=reminder.enabled,
        scheduled_at=reminder.scheduled_at,
        sent_at=reminder.sent_at,
        acted_at=reminder.acted_at,
        label=format_reminder_label(deadline, reminder.scheduled_at),
    )


def to_task_summary(task: Task) -> TaskSummary:
    return TaskSummary(
        id=task.id,
        title=task.title,
        status=task.status,
        needs_help=task.needs_help,
        deadline=task.deadline,
    )


def to_task_response(task: Task) -> TaskResponse:
    assignees: list[UserResponse] = []
    for user in task.assignees:
        assignees.append(to_user_response(user))

    group_id = None
    if task.project is not None:
        group_id = task.project.group_id

    related_tasks: list[TaskSummary] = []
    for related in task.related_tasks:
        related_tasks.append(to_task_summary(related))

    reminders: list[ReminderResponse] = []
    for reminder in task.reminders:
        reminders.append(to_reminder_response(reminder, task.deadline))

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        status=task.status,
        is_priority=task.is_priority,
        needs_help=task.needs_help,
        deadline=task.deadline,
        user_id=task.user_id,
        project_id=task.project_id,
        group_id=group_id,
        has_photo=any(attachment.kind == AttachmentKind.PHOTO for attachment in task.attachments),
        assignees=assignees,
        related_tasks=related_tasks,
        reminders=reminders,
    )


def to_time_block_response(time_block: TimeBlock) -> TimeBlockResponse:
    return TimeBlockResponse(
        id=time_block.id,
        start_at=time_block.start_at,
        end_at=time_block.end_at,
        task_id=time_block.task_id,
    )


def to_group_response(group: Group, pending_task_count: int = 0) -> GroupResponse:
    users: list[UserResponse] = []
    for user in group.users:
        users.append(to_user_response(user))
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        deadline=group.deadline,
        users=users,
        pending_task_count=pending_task_count,
    )


def to_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        deadline=project.deadline,
        group_id=project.group_id,
    )
