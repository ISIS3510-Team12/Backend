from typing import Annotated
from fastapi import Depends
from app.core.dependencies.repositories import UserRepositoryDep, TaskRepositoryDep, GroupRepositoryDep
from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.services.group_service import GroupService

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



