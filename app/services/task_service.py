from datetime import datetime
from app.core.consts import TaskEventType, TaskStatus
from app.models import Task, TimeBlock, Reminder, Attachment, TaskEvent
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.exceptions import ProjectNotFoundException, TaskExistsException, TaskNotFoundException
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.services.mappers import to_task_response

class TaskService:
    def __init__(
        self, 
        repository: TaskRepository,
        project_repository: ProjectRepository
    ):
        self.repository = repository
        self.project_repository = project_repository

    def get_task_or_raise(self, task_id: int, user_id: int) -> Task:
        task = self.repository.get_task_by_user_id(task_id, user_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return task

    def register_event(
        self,
        event_type: TaskEventType,
        task_status: TaskStatus,
        task_id: int,
        user_id: int,
    ) -> None:
        task_event = TaskEvent(
            event_type=event_type,
            task_status=task_status,
            occurred_at=datetime.now(),
            task_id=task_id,
            author_id=user_id,
        )
        self.repository.register_task_event(task_event)

    def create_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        project = None
        if data.project_id:
            project = self.project_repository.get_project_by_id(data.project_id)

        if project is None and data.project_id is not None:
            raise ProjectNotFoundException(data.project_id)
        
        task = Task(
            title=data.title,
            description=data.description,
            task_type=data.task_type,
            status=TaskStatus.NOT_STARTED,
            is_priority=data.is_priority,
            needs_help=data.needs_help,
            deadline=data.deadline,
            user_id=user_id,
            project_id=data.project_id
        )
        created_task = self.repository.create_task(task)

        # TODO: persist data.assignee_ids onto TaskAssignee and
        # data.related_task_ids onto TaskRelation once the write layer exists.

        self.register_event(
            TaskEventType.CREATED, created_task.status, created_task.id, user_id
        )

        return to_task_response(created_task)

    def get_tasks_by_user(self, user_id: int) -> list[TaskResponse]:
        tasks = self.repository.get_all_tasks_by_user(user_id)
        responses: list[TaskResponse] = []
        for task in tasks:
            responses.append(to_task_response(task))
        return responses

    def get_task_by_user(self, task_id: int, user_id: int) -> TaskResponse:
        task = self.get_task_or_raise(task_id, user_id)
        self.register_event(TaskEventType.VIEWED, task.status, task_id, user_id)
        return to_task_response(task)

    def get_tasks_by_project(self, project_id: int, user_id: int) -> list[TaskResponse]:
        project = self.project_repository.get_project_by_id(project_id, user_id)
        if project is None:
            raise ProjectNotFoundException(project_id)
        
        tasks = self.repository.get_all_tasks_by_project(project_id)
        responses: list[TaskResponse] = []
        for task in tasks:
            responses.append(to_task_response(task))
        return responses

    def get_task_by_project(self, task_id: int, user_id: int, project_id: int) -> TaskResponse:
        project = self.project_repository.get_project_by_id(project_id, user_id)
        if project is None:
            raise ProjectNotFoundException(project_id)
        task = self.repository.get_task_by_project(project_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        self.register_event(TaskEventType.VIEWED, task.status, task_id, user_id)
        return to_task_response(task)

    def update_task(self, task_id: int, user_id: int, data: TaskUpdate) -> TaskResponse:
        task = self.get_task_or_raise(task_id, user_id)

        if data.project_id is not None:
            project = self.project_repository.get_project_by_id(data.project_id)
            if project is None:
                raise ProjectNotFoundException(data.project_id)

        # assignee_ids / related_task_ids are relationship updates, handled by the
        # (pending) write layer rather than as scalar columns.
        fields = data.model_dump(exclude_unset=True, exclude={"assignee_ids", "related_task_ids"})
        updated_task = self.repository.update_task(task, fields)

        self.register_event(
            TaskEventType.UPDATED, updated_task.status, updated_task.id, user_id
        )

        return to_task_response(updated_task)

    def change_task_status(self, task_id: int, user_id: int, new_status: TaskStatus) -> TaskResponse:
        new_status = TaskStatus(new_status)
        task = self.get_task_or_raise(task_id, user_id)
        old_status = task.status

        updated_task = self.repository.update_task(task, {"status": new_status})

        if old_status != new_status:
            self.register_event(
                TaskEventType.STATUS_CHANGED, new_status, updated_task.id, user_id
            )

        return to_task_response(updated_task)

    def delete_task(self, task_id: int, user_id: int) -> None:
        task = self.get_task_or_raise(task_id, user_id)
        self.repository.delete_task(task)
        self.register_event(TaskEventType.DELETED, task.status, task_id, user_id)

    def get_task_events_by_task(self, task_id: int) -> list[TaskEvent]:
        task = self.repository.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return self.repository.get_task_events_by_task_id(task.id)
    
    def get_task_events_by_user(self, user_id: int) -> list[TaskEvent]:
        return self.repository.get_task_events_by_user_id(user_id)
