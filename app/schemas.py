from datetime import datetime

from pydantic import BaseModel
from app.core.consts import TaskStatus

class UserCreate(BaseModel):
    first_name: str
    last_name: str

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

class UserPreferencesUpdate(BaseModel):
    push_enabled: bool | None = None

class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str

class ReminderCreate(BaseModel):
    scheduled_at: datetime
    enabled: bool = True

class ReminderUpdate(BaseModel):
    scheduled_at: datetime | None = None
    enabled: bool | None = None

class ReminderResponse(BaseModel):
    id: int
    enabled: bool
    scheduled_at: datetime
    sent_at: datetime | None = None
    acted_at: datetime | None = None
    # Humanised offset from the owning task's deadline
    label: str | None = None

class TimeBlockCreate(BaseModel):
    start_at: datetime
    end_at: datetime

class TimeBlockUpdate(BaseModel):
    start_at: datetime | None = None
    end_at: datetime | None = None

class TimeBlockResponse(BaseModel):
    id: int
    start_at: datetime
    end_at: datetime
    task_id: int

class TaskCreate(BaseModel):
    title: str
    task_type: str
    description: str | None = None
    is_priority: bool = False
    needs_help: bool = False
    deadline: datetime
    project_id: int | None = None
    assignee_ids: list[str] = []
    related_task_ids: list[int] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Finish the report",
                "task_type": "Work",
                "description": "Deliverable link and notes",
                "is_priority": True,
                "needs_help": False,
                "deadline": "2024-06-30T17:00:00Z",
                "project_id": 1,
                "assignee_ids": ["user_123"],
                "related_task_ids": [2, 3]
            }
        }
    }

class TaskUpdate(BaseModel):
    title: str | None = None
    task_type: str | None = None
    description: str | None = None
    is_priority: bool | None = None
    needs_help: bool | None = None
    deadline: datetime | None = None
    project_id: int | None = None
    assignee_ids: list[str] | None = None
    related_task_ids: list[int] | None = None

class TaskSummary(BaseModel):
    """A lightweight task reference (used for related tasks to avoid recursion)."""
    id: int
    title: str
    status: TaskStatus
    needs_help: bool = False
    deadline: datetime | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    task_type: str
    status: TaskStatus
    is_priority: bool = False
    needs_help: bool = False
    deadline: datetime | None = None
    user_id: str
    project_id: int | None = None
    group_id: int | None = None
    has_photo: bool = False
    assignees: list[UserResponse] = []
    related_tasks: list[TaskSummary] = []
    reminders: list[ReminderResponse] = []

class GroupCreate(BaseModel):
    name: str
    description: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Group name #1",
                "description": "Course project group"
            }
        }
    }

class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    
class GroupResponse(BaseModel):
    id: int
    name: str
    description: str
    users: list[UserResponse]
    pending_task_count: int = 0

class ProjectCreate(BaseModel):
    name: str
    description: str
    deadline: datetime
    group_id: int

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    group_id: int | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    deadline: datetime
    group_id: int
