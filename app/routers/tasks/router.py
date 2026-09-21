from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session

from app.core.consts import (
    DEFAULT_URGENT_WINDOW_HOURS,
    MAX_URGENT_WINDOW_HOURS,
    MIN_URGENT_WINDOW_HOURS,
)
from app.core.dependencies import CurrentUser
from app.db import get_db
from app.models import Task
from app.services.tasks import (
    estimate_task_duration,
    get_urgent_tasks,
    user_can_access_task,
)

router = APIRouter(
    prefix="/tasks",
)


class DurationEstimateResponse(BaseModel):
    task_id: int
    suggested_duration_minutes: int
    current_estimate_minutes: int
    sample_size: int
    based_on: str


class UrgentTaskResponse(BaseModel):
    task_id: int
    title: str
    project_id: int
    project_name: str
    deadline: datetime
    hours_left: float
    priority: str
    status: str


class UrgentTasksResponse(BaseModel):
    within_hours: int
    count: int
    tasks: list[UrgentTaskResponse]


@router.get(
    "/urgent",
    response_model=UrgentTasksResponse,
)
def get_urgent_tasks_endpoint(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    within_hours: int = Query(
        default=DEFAULT_URGENT_WINDOW_HOURS,
        ge=MIN_URGENT_WINDOW_HOURS,
        le=MAX_URGENT_WINDOW_HOURS,
    ),
) -> UrgentTasksResponse:
    """
    Context aware feature. It lists pending tasks whose project deadline is close.
    """
    urgent_tasks = get_urgent_tasks(db, current_user, within_hours)

    return UrgentTasksResponse(
        within_hours=within_hours,
        count=len(urgent_tasks),
        tasks=urgent_tasks,
    )


@router.get(
    "/{task_id}/duration-estimate",
    response_model=DurationEstimateResponse,
)
def get_duration_estimate_endpoint(
    task_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
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
