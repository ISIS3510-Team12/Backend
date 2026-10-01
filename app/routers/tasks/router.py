from fastapi import APIRouter, Response, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import TaskServiceDep
from app.schemas import (
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TimeBlockCreate,
    TimeBlockResponse,
    TimeBlockUpdate,
)

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

@router.get("/own/{group_id}", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_own_tasks(
    group_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_own_tasks(current_user.user_id, group_id)

@router.get("/group/{group_id}", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_group_tasks(
    group_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_group_tasks(current_user.user_id, group_id)

@router.get("/all", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(
    current_user: CurrentUser,
    service: TaskServiceDep,
    due_within_days: int | None = None,
    mine: bool = False,
    priority: bool = False
):
    return service.get_all_tasks(current_user.user_id, due_within_days, mine, priority)

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
    data: TaskUpdate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.update_task(task_id, current_user.user_id, data)

@router.patch("/{task_id}/status", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def change_task_status(
    task_id: int,
    status: str,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.change_task_status(task_id, current_user.user_id, status)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    service.delete_task(task_id, current_user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Reminders -----------------------------------------------------------

@router.get(
    "/{task_id}/reminders",
    response_model=list[ReminderResponse],
    status_code=status.HTTP_200_OK,
)
def get_reminders(
    task_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_reminders(task_id, current_user.user_id)

@router.post(
    "/{task_id}/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reminder(
    task_id: int,
    data: ReminderCreate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.create_reminder(task_id, current_user.user_id, data)

@router.patch(
    "/{task_id}/reminders/{reminder_id}",
    response_model=ReminderResponse,
    status_code=status.HTTP_200_OK,
)
def update_reminder(
    task_id: int,
    reminder_id: int,
    data: ReminderUpdate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.update_reminder(task_id, reminder_id, current_user.user_id, data)

@router.delete(
    "/{task_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reminder(
    task_id: int,
    reminder_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    service.delete_reminder(task_id, reminder_id, current_user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Time blocks ---------------------------------------------------------

@router.get(
    "/{task_id}/time-blocks",
    response_model=list[TimeBlockResponse],
    status_code=status.HTTP_200_OK,
)
def get_time_blocks(
    task_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.get_time_blocks(task_id, current_user.user_id)

@router.post(
    "/{task_id}/time-blocks",
    response_model=TimeBlockResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_time_block(
    task_id: int,
    data: TimeBlockCreate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.create_time_block(task_id, current_user.user_id, data)

@router.patch(
    "/{task_id}/time-blocks/{time_block_id}",
    response_model=TimeBlockResponse,
    status_code=status.HTTP_200_OK,
)
def update_time_block(
    task_id: int,
    time_block_id: int,
    data: TimeBlockUpdate,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    return service.update_time_block(task_id, time_block_id, current_user.user_id, data)

@router.delete(
    "/{task_id}/time-blocks/{time_block_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_time_block(
    task_id: int,
    time_block_id: int,
    current_user: CurrentUser,
    service: TaskServiceDep
):
    service.delete_time_block(task_id, time_block_id, current_user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
