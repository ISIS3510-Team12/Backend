from app.core.consts import (
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_NOT_STARTED,
    EventType,
)
from app.models import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_event_repository import TaskEventRepository
from app.repositories.task_repository import TaskRepository
from app.exceptions import ProjectNotFoundException, TaskNotFoundException
from app.schemas import TaskCreate, TaskUpdate


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        project_repository: ProjectRepository,
        task_event_repository: TaskEventRepository,
    ):
        self.repository = repository
        self.project_repository = project_repository
        self.task_event_repository = task_event_repository

    def create_task(self, user_id: str, data: TaskCreate) -> Task:
        if data.project_id is not None:
            project = self.project_repository.get_project_by_id(data.project_id)
            if project is None:
                raise ProjectNotFoundException(data.project_id)

        task = Task(
            title=data.title,
            task_type=data.task_type,
            status=STATUS_NOT_STARTED,
            is_priority=data.is_priority,
            deadline=data.deadline,
            user_id=user_id,
            project_id=data.project_id,
        )

        created_task = self.repository.create_task(task)
        self.task_event_repository.add_event(created_task.id, EventType.CREATED)
        return created_task

    def get_tasks(self, user_id: str) -> list[Task]:
        return self.repository.get_all_tasks_by_user(user_id)

    def get_task(self, task_id: int, user_id: str) -> Task:
        task = self.repository.get_task_by_id(task_id, user_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return task

    def update_task(self, task_id: int, user_id: str, data: TaskUpdate) -> Task:
        task = self.get_task(task_id, user_id)

        if data.project_id is not None:
            project = self.project_repository.get_project_by_id(data.project_id)
            if project is None:
                raise ProjectNotFoundException(data.project_id)

        previous_status = task.status
        update_data = data.model_dump(exclude_unset=True)

        updated_task = self.repository.update_task(task, update_data)

        new_status = update_data.get("status")
        if new_status is not None and new_status != previous_status:
            if new_status == STATUS_IN_PROGRESS:
                self.task_event_repository.add_event(task.id, EventType.STARTED)
            elif new_status == STATUS_COMPLETED:
                self.task_event_repository.add_event(task.id, EventType.COMPLETED)

        return updated_task

    def delete_task(self, task_id: int, user_id: str) -> None:
        task = self.get_task(task_id, user_id)
        self.repository.delete_task(task)
