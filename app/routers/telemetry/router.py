from fastapi import APIRouter, status

from app.core.dependencies.services import TaskServiceDep

router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"]
)

@router.get("/{task_id}/events", status_code=status.HTTP_200_OK)
def get_task_events(
    task_id: int,
    service: TaskServiceDep
):
    return service.get_task_events_by_task(task_id)

@router.get("/users/{user_id}/events", status_code=status.HTTP_200_OK)
def get_user_task_events(
    user_id: int,
    service: TaskServiceDep
):
    return service.get_task_events_by_user(user_id)