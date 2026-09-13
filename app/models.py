from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

class UserGroup(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.user_id", primary_key=True)
    group_id: int = Field(foreign_key="group.id", primary_key=True)

class User(SQLModel, table=True):
    user_id: str = Field(primary_key=True, index=True)
    first_name: str
    last_name: str
    major: str
    auth_provider: str
    last_active_at: datetime
    
    groups: list["Group"] = Relationship(
        back_populates="users",
        link_model=UserGroup,
    )
    preferences: "UserPreferences" = Relationship(
        back_populates="user",
    )
    tasks: list["Task"] = Relationship(
        back_populates="owner",
    )

class UserPreferences(SQLModel, table=True):
    user_id: str = Field(
        foreign_key="user.user_id",
        primary_key=True,
        index=True
    )

    push_enabled: bool = True

    user: User = Relationship(
        back_populates="preferences",
    )

    
class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    deadline: datetime
    
    users: list[User] = Relationship(
        back_populates="groups",
        link_model=UserGroup,
    )
    projects: list["Project"] = Relationship(
        back_populates="group",
    )

class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    deadline: datetime
    group_id: int = Field(foreign_key="group.id")

    group: Group = Relationship(
        back_populates="projects",
    )
    tasks: list["Task"] = Relationship(
        back_populates="project",
    )

class Task(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    title: str
    task_type: str
    status: str
    priority: str
    difficulty: str
    estimated_duration: int

    # Owner
    user_id: str = Field(
        foreign_key="user.user_id",
        index=True,
    )

    project_id: int = Field(
        foreign_key="project.id",
        index=True,
    )

    owner: User = Relationship(
        back_populates="tasks",
    )

    project: Project = Relationship(
        back_populates="tasks",
    )

    # Related entities
    time_blocks: list["TimeBlock"] = Relationship(
        back_populates="task",
    )

    reminders: list["Reminder"] = Relationship(
        back_populates="task",
    )

    attachments: list["Attachment"] = Relationship(
        back_populates="task",
    )

    events: list["TaskEvent"] = Relationship(
        back_populates="task",
    )
    
class TimeBlock(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    start_at: datetime
    end_at: datetime

    task_id: int = Field(
        foreign_key="task.id",
        index=True,
    )

    task: Task = Relationship(
        back_populates="time_blocks",
    )

class Reminder(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    kind: str
    scheduled_at: datetime
    sent_at: datetime | None = None
    acted_at: datetime | None = None

    task_id: int = Field(
        foreign_key="task.id",
        index=True,
    )

    task: Task = Relationship(
        back_populates="reminders",
    )

class Attachment(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    kind: str
    bucket: str
    key: str
    last_modified_date: datetime

    task_id: int = Field(
        foreign_key="task.id",
        index=True,
    )

    task: Task = Relationship(
        back_populates="attachments",
    )

class TaskEvent(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    event_type: str
    occurred_at: datetime

    task_id: int = Field(
        foreign_key="task.id",
        index=True,
    )

    task: Task = Relationship(
        back_populates="events",
    )
