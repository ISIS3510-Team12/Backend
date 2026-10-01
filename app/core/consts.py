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
ALLOWED_PHOTO_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})

EVENT_STARTED = "started"
EVENT_COMPLETED = "completed"

DEFAULT_URGENT_WINDOW_HOURS = 24
MIN_URGENT_WINDOW_HOURS = 1
MAX_URGENT_WINDOW_HOURS = 168

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600

BASED_ON_HISTORY = "historical_events"
BASED_ON_FALLBACK = "task_estimate"