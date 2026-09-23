from datetime import datetime
from app.core.consts import TaskEventType, TaskStatus
from app.models import Task, TimeBlock, Reminder, Attachment, TaskEvent
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
            status=TaskStatus.NOT_STARTED,
            is_priority=data.is_priority,
            deadline=data.deadline,
            user_id=user_id,
            project_id=data.project_id,
        )
        created_task = self.repository.create_task(task)

        task_event = TaskEvent(
            event_type=TaskEventType.CREATED,
            occurred_at=datetime.now(),
            task_id=created_task.id,
            author_id=user_id,
        )
        self.repository.register_task_event(task_event)

        return created_task

    def get_tasks(self, user_id: str) -> list[Task]:
        return self.repository.get_all_tasks_by_user(user_id)

    def get_task(self, task_id: int, user_id: str) -> Task:
        task = self.repository.get_task_by_user_id(task_id, user_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        task_event = TaskEvent(
            event_type=TaskEventType.VIEWED,
            occurred_at=datetime.now(),
            task_id=task_id,
            author_id=user_id,
        )
        self.repository.register_task_event(task_event)
        return task

    def update_task(self, task_id: int, user_id: str, data: TaskUpdate) -> Task:
        task = self.get_task(task_id, user_id)

        if data.project_id is not None:
            project = self.project_repository.get_project_by_id(data.project_id)
            if project is None:
                raise ProjectNotFoundException(data.project_id)

        update_data = data.model_dump(exclude_unset=True)
        updated_task = self.repository.update_task(task, update_data)

        task_event = TaskEvent(
            event_type=TaskEventType.UPDATED,
            occurred_at=datetime.now(),
            task_id=updated_task.id,
            author_id=user_id,
        )
        self.repository.register_task_event(task_event)

        return updated_task

    def delete_task(self, task_id: int, user_id: str) -> None:
        task = self.get_task(task_id, user_id)
        self.repository.delete_task(task)
        task_event = TaskEvent(
            event_type=TaskEventType.DELETED,
            occurred_at=datetime.now(),
            task_id=task_id,
            author_id=user_id,
        )
        self.repository.register_task_event(task_event)

    def get_task_events_by_task(self, task_id: int) -> list[TaskEvent]:
        task = self.repository.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return self.repository.get_task_events_by_task_id(task.id)

    def get_task_events_by_user(self, user_id: int) -> list[TaskEvent]:
        return self.repository.get_task_events_by_user_id(user_id)
