from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.database import DatabaseSession
from app.core.dependencies.services import TaskServiceDep
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate
from app.services.tasks import estimate_task_duration, user_can_access_task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


class DurationEstimateResponse(BaseModel):
    task_id: int
    suggested_duration_minutes: int
    current_estimate_minutes: int
    sample_size: int
    based_on: str


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.create_task(current_user.user_id, data)


@router.get("", status_code=status.HTTP_200_OK)
def get_tasks(
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_tasks(current_user.user_id)


@router.get(
    "/{task_id}/duration-estimate",
    response_model=DurationEstimateResponse,
)
def get_duration_estimate_endpoint(
    task_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> DurationEstimateResponse:
    """
    Smart feature. It suggests a realistic duration for a task from past activity.
    """
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if not user_can_access_task(db, task, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this task",
        )

    estimate = estimate_task_duration(db, task, current_user)

    return DurationEstimateResponse(
        task_id=task_id,
        suggested_duration_minutes=estimate["suggested_duration_minutes"],
        current_estimate_minutes=estimate["current_estimate_minutes"],
        sample_size=estimate["sample_size"],
        based_on=estimate["based_on"],
    )


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
def get_task(
    task_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_task(task_id, current_user.user_id)


@router.patch("/{task_id}", status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.update_task(task_id, current_user.user_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    service.delete_task(task_id, current_user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
