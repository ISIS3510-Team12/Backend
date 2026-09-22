from datetime import datetime

from pydantic import BaseModel

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
    
class TaskUpdate(BaseModel):
    title: str | None = None
    task_type: str | None = None
    is_priority: str | None = None
    deadline: datetime | None = None
    project_id: int | None = None