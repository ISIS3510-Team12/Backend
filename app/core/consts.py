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

class AttachmentKind(StrEnum):
    PHOTO = "photo"

MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_CONTENT_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
)

SECONDS_PER_DAY = 86400

MAX_NOTIFY_WITHIN_METERS = 1000

# Task detail visits shorter than this are treated as accidental taps.
MIN_TASK_DETAIL_SESSION_SECONDS = 1
