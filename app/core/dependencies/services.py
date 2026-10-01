from typing import Annotated
from fastapi import Depends
from app.core.dependencies.repositories import TaskEventRepositoryDep, UserRepositoryDep, TaskRepositoryDep, GroupRepositoryDep, ProjectRepositoryDep, AnalyticsRepositoryDep
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.services.group_service import GroupService
from app.services.project_service import ProjectService
from app.analytics.analytics_service import AnalyticsService
from app.core.dependencies.external import S3ClientDep

def get_user_service(repo: UserRepositoryDep, s3_client: S3ClientDep) -> UserService:
    return UserService(repo, s3_client)

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]

def get_task_service(
    repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
    user_repo: UserRepositoryDep,
    task_event_repo: TaskEventRepositoryDep) -> TaskService:
    return TaskService(repo, project_repo, user_repo)

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

def get_analytics_service(repo: AnalyticsRepositoryDep) -> AnalyticsService:
    return AnalyticsService(repo)

AnalyticsServiceDep = Annotated[
    AnalyticsService,
    Depends(get_analytics_service),
]

def get_notification_service(repo: TaskEventRepositoryDep) -> NotificationService:
    return NotificationService(repo)


NotificationServiceDep = Annotated[
    NotificationService,
    Depends(get_notification_service),
]
