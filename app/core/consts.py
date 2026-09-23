from enum import Enum, StrEnum


class TaskStatus(StrEnum):
    COMPLETED = "completed"
    NOT_STARTED = "not started"
    IN_PROGRESS = "in_progress"


class TaskEventType(StrEnum):
    CREATED = "created"
    VIEWED = "viewed"
    UPDATED = "updated"
    DELETED = "deleted"


class EventType(str, Enum):
    CREATED = "created"
    STARTED = "started"
    COMPLETED = "completed"
    NEEDS_HELP = "needs_help"


class NotificationKind(str, Enum):
    DEADLINE_SOON = "deadline_soon"
    NEEDS_HELP = "needs_help"
    PRIORITY = "priority"


def enum_values(enum_class: type[Enum]) -> list[str]:
    values: list[str] = []
    for member in enum_class:
        values.append(member.value)
    return values


NOTIFICATION_WINDOW_HOURS = 24

SECONDS_PER_MINUTE = 60

DEFAULT_TASK_DURATION_MINUTES = 60

BASED_ON_HISTORY = "historical_events"
BASED_ON_FALLBACK = "task_estimate"
