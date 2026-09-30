from datetime import datetime
from app.core.consts import TaskEventType, TaskStatus
from app.models import Reminder, Task, TaskEvent, TimeBlock
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.exceptions import (
    ProjectNotFoundException,
    ReminderNotFoundException,
    TaskExistsException,
    TaskNotFoundException,
    TimeBlockNotFoundException,
    UserNotFoundException,
)
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
from app.services.mappers import to_reminder_response, to_task_response, to_time_block_response

class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.project_repository = project_repository
        self.user_repository = user_repository

    def get_task_or_raise(self, task_id: int, user_id: int) -> Task:
        task = self.repository.get_task_for_user(task_id, user_id)
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

    def _validate_assignees(self, user_ids: list[str]) -> None:
        for user_id in user_ids:
            if self.user_repository.get_by_id(user_id) is None:
                raise UserNotFoundException(user_id)

    def _validate_related_tasks(self, task: Task, related_task_ids: list[int]) -> None:
        for related_id in related_task_ids:
            if self.repository.get_task_by_user_id(related_id, task.user_id) is None:
                raise TaskNotFoundException(related_id)

    def _apply_relationships(self, task: Task, data: TaskCreate | TaskUpdate) -> None:
        """Persist assignees / related tasks when the request provided them."""
        provided = data.model_dump(exclude_unset=True)

        if "assignee_ids" in provided:
            assignee_ids = provided.get("assignee_ids") or []
            self._validate_assignees(assignee_ids)
            self.repository.replace_assignees(task, assignee_ids)

        if "related_task_ids" in provided:
            related_ids: list[int] = []
            for related_id in provided.get("related_task_ids") or []:
                if related_id != task.id:
                    related_ids.append(related_id)
            self._validate_related_tasks(task, related_ids)
            self.repository.replace_related_tasks(task, related_ids)

    def create_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        project = None
        if data.project_id:
            project = self.project_repository.get_project_by_id(data.project_id, user_id)

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

        self._apply_relationships(created_task, data)

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

    def get_own_tasks(self, user_id: str, group_id: int) -> list[TaskResponse]:
        """Tasks in the group where the user is the owner or an assignee."""
        tasks = self.repository.get_own_tasks_by_group(user_id, group_id)
        responses: list[TaskResponse] = []
        for task in tasks:
            responses.append(to_task_response(task))
        return responses

    def get_group_tasks(self, user_id: str, group_id: int) -> list[TaskResponse]:
        """Tasks in the group where the user is neither the owner nor an assignee."""
        tasks = self.repository.get_group_tasks_by_group(user_id, group_id)
        responses: list[TaskResponse] = []
        for task in tasks:
            responses.append(to_task_response(task))
        return responses

    def get_all_tasks(self, user_id: str) -> list[TaskResponse]:
        """Every task in any group the user belongs to."""
        tasks = self.repository.get_all_tasks_by_user_groups(user_id)
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
            project = self.project_repository.get_project_by_id(data.project_id, user_id)
            if project is None:
                raise ProjectNotFoundException(data.project_id)

        # Scalar columns only; relationships are handled separately below.
        fields = data.model_dump(exclude_unset=True, exclude={"assignee_ids", "related_task_ids"})
        updated_task = self.repository.update_task(task, fields)

        self._apply_relationships(updated_task, data)

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

    # --- Reminders -------------------------------------------------------

    def get_reminders(self, task_id: int, user_id: int) -> list[ReminderResponse]:
        task = self.get_task_or_raise(task_id, user_id)
        reminders = self.repository.get_reminders_by_task(task_id)
        responses: list[ReminderResponse] = []
        for reminder in reminders:
            responses.append(to_reminder_response(reminder, task.deadline))
        return responses

    def create_reminder(
        self, task_id: int, user_id: int, data: ReminderCreate
    ) -> ReminderResponse:
        task = self.get_task_or_raise(task_id, user_id)
        reminder = Reminder(
            scheduled_at=data.scheduled_at,
            enabled=data.enabled,
            task_id=task.id,
        )
        created = self.repository.create_reminder(reminder)
        return to_reminder_response(created, task.deadline)

    def update_reminder(
        self, task_id: int, reminder_id: int, user_id: int, data: ReminderUpdate
    ) -> ReminderResponse:
        task = self.get_task_or_raise(task_id, user_id)
        reminder = self.repository.get_reminder_by_task(reminder_id, task_id)
        if reminder is None:
            raise ReminderNotFoundException(reminder_id)
        updated = self.repository.update_reminder(reminder, data.model_dump(exclude_unset=True))
        return to_reminder_response(updated, task.deadline)

    def delete_reminder(self, task_id: int, reminder_id: int, user_id: int) -> None:
        self.get_task_or_raise(task_id, user_id)
        reminder = self.repository.get_reminder_by_task(reminder_id, task_id)
        if reminder is None:
            raise ReminderNotFoundException(reminder_id)
        self.repository.delete_reminder(reminder)

    # --- Time blocks -----------------------------------------------------

    def get_time_blocks(self, task_id: int, user_id: int) -> list[TimeBlockResponse]:
        self.get_task_or_raise(task_id, user_id)
        time_blocks = self.repository.get_time_blocks_by_task(task_id)
        responses: list[TimeBlockResponse] = []
        for time_block in time_blocks:
            responses.append(to_time_block_response(time_block))
        return responses

    def create_time_block(
        self, task_id: int, user_id: int, data: TimeBlockCreate
    ) -> TimeBlockResponse:
        task = self.get_task_or_raise(task_id, user_id)
        time_block = TimeBlock(
            start_at=data.start_at,
            end_at=data.end_at,
            task_id=task.id,
        )
        created = self.repository.create_time_block(time_block)
        return to_time_block_response(created)

    def update_time_block(
        self, task_id: int, time_block_id: int, user_id: int, data: TimeBlockUpdate
    ) -> TimeBlockResponse:
        self.get_task_or_raise(task_id, user_id)
        time_block = self.repository.get_time_block_by_task(time_block_id, task_id)
        if time_block is None:
            raise TimeBlockNotFoundException(time_block_id)
        updated = self.repository.update_time_block(
            time_block, data.model_dump(exclude_unset=True)
        )
        return to_time_block_response(updated)

    def delete_time_block(self, task_id: int, time_block_id: int, user_id: int) -> None:
        self.get_task_or_raise(task_id, user_id)
        time_block = self.repository.get_time_block_by_task(time_block_id, task_id)
        if time_block is None:
            raise TimeBlockNotFoundException(time_block_id)
        self.repository.delete_time_block(time_block)

    # --- Telemetry -------------------------------------------------------

    def get_task_events_by_task(self, task_id: int) -> list[TaskEvent]:
        task = self.repository.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return self.repository.get_task_events_by_task_id(task.id)
    
    def get_task_events_by_user(self, user_id: int) -> list[TaskEvent]:
        return self.repository.get_task_events_by_user_id(user_id)
