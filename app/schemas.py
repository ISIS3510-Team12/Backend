from datetime import datetime

from pydantic import BaseModel
from app.core.consts import TaskStatus

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    major: str

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    major: str | None = None
    email: str | None = None

class UserPreferencesUpdate(BaseModel):
    push_enabled: bool | None = None
    
class TaskCreate(BaseModel):
    title: str
    task_type: str
    is_priority: bool = False
    deadline: datetime
    project_id: int | None = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Finish the report",
                "task_type": "Work",
                "is_priority": True,
                "deadline": "2024-06-30T17:00:00Z",
                "project_id": 1
            }
        }
    }
    
class TaskUpdate(BaseModel):
    title: str | None = None
    task_type: str | None = None
    is_priority: str | None = None
    deadline: datetime | None = None
    project_id: int | None = None
    status: TaskStatus | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    task_type: str
    status: TaskStatus
    is_priority: bool = False
    needs_help: bool = False
    deadline: datetime | None = None