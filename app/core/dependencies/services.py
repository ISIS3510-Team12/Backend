from typing import Annotated
from fastapi import Depends
from app.core.dependencies.repositories import UserRepositoryDep, TaskRepositoryDep, GroupRepositoryDep, ProjectRepositoryDep
from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.services.group_service import GroupService
from app.services.project_service import ProjectService

def get_user_service(repo: UserRepositoryDep) -> UserService:
    return UserService(repo)

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]

def get_task_service(repo: TaskRepositoryDep) -> TaskService:
    return TaskService(repo)

TaskServiceDep = Annotated[
    TaskService,
    Depends(get_task_service),
]

def get_group_service(repo: GroupRepositoryDep) -> GroupService:
    return GroupService(repo)

GroupServiceDep = Annotated[
    GroupService,
    Depends(get_group_service),
]

def get_project_service(repo: ProjectRepositoryDep) -> ProjectService:
    return ProjectService(repo)

ProjectServiceDep = Annotated[
    ProjectService,
    Depends(get_project_service),
]



