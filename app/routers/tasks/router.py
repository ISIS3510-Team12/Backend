from fastapi import APIRouter, Response, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import TaskServiceDep
from app.schemas import TaskCreate, TaskResponse

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.create_task(current_user.user_id, data)

@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks_by_user(
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_tasks_by_user(current_user.user_id)

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_user(
    task_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_task_by_user(task_id, current_user.user_id)

@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    data: TaskCreate,
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