from fastapi import APIRouter, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import TaskServiceDep, TelemetryServiceDep
from app.schemas import ScreenLoadEventCreate, TaskDetailSessionCreate, TaskDetailSessionResponse

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
    user_id: str,
    service: TaskServiceDep
):
    return service.get_task_events_by_user(user_id)

@router.post("/screen-load", status_code=status.HTTP_201_CREATED)
def register_screen_load(
    data: ScreenLoadEventCreate,
    current_user: CurrentUser,
    service: TelemetryServiceDep,
):
    return service.register_screen_load(current_user.user_id, data)


@router.post("/task-detail-session", response_model=TaskDetailSessionResponse, status_code=status.HTTP_201_CREATED)
def register_task_detail_session(
    data: TaskDetailSessionCreate,
    current_user: CurrentUser,
    service: TelemetryServiceDep,
):
    return service.register_task_detail_session(current_user.user_id, data)
