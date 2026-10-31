from enum import StrEnum

class TaskStatus(StrEnum):
    COMPLETED = "completed"
    NOT_STARTED = "not started"
    IN_PROGRESS = "in_progress"
    
class TaskEventType(StrEnum):
    CREATED = "created"
    VIEWED = "viewed"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    DELETED = "deleted"

class NextTaskReason(StrEnum):
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    DUE_SOON = "due_soon"
    PRIORITY = "priority"
    NEEDS_HELP = "needs_help"
    NEXT_DEADLINE = "next_deadline"

class AttachmentKind(StrEnum):
    PHOTO = "photo"

MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_CONTENT_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
)

SECONDS_PER_DAY = 86400

# How far ahead the Next Task recommendation looks. Overdue tasks are included.
NEXT_TASK_HORIZON_DAYS = 14

# Projects at or above this percentile of completed tasks count as highly active.
HIGH_ACTIVITY_PROJECT_PERCENTILE = 0.75

MAX_NOTIFY_WITHIN_METERS = 1000

# Task detail visits shorter than this are treated as accidental taps.
MIN_TASK_DETAIL_SESSION_SECONDS = 1

# Reopening the same task this many times in a day means one initial open plus
# this many returns to the task detail screen.
MIN_TASK_REOPENS_PER_DAY = 3
