from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import DatabaseSession
from app.repositories.user_repository import UserRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.project_repository import ProjectRepository

def get_user_repository(db: DatabaseSession) -> UserRepository:
    return UserRepository(db)

UserRepositoryDep = Annotated[
    UserRepository,
    Depends(get_user_repository),
]

def get_task_repository(db: DatabaseSession) -> TaskRepository:
    return TaskRepository(db)

TaskRepositoryDep = Annotated[
    TaskRepository,
    Depends(get_task_repository),
]

def get_group_repository(db: DatabaseSession) -> GroupRepository:
    return GroupRepository(db)

GroupRepositoryDep = Annotated[
    GroupRepository,
    Depends(get_group_repository),
]

def get_project_repository(db: DatabaseSession) -> ProjectRepository:
    return ProjectRepository(db)

ProjectRepositoryDep = Annotated[
    ProjectRepository,
    Depends(get_project_repository),
]