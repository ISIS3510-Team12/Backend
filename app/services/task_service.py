from app.models import Task, TimeBlock, Reminder, Attachment, TaskEvent
from app.repositories.task_repository import TaskRepository
from app.exceptions import TaskExistsException, TaskNotFoundException

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id:str ,task: Task) -> Task:
        ...

    def create_time_block(self, task_id: int, time_block: TimeBlock) -> TimeBlock:
        ...

    def create_reminder(self, task_id: int, reminder: Reminder) -> Reminder:
        ...

    def create_attachment(self, task_id: int, attachment: Attachment) -> Attachment:
        ...

    def create_task_event(self, task_id: int, task_event: TaskEvent) -> TaskEvent:
        ...

    def get_task_by_user_id(self, user_id: str, task_id: int) -> Task:
        ...

    def get_task_time_blocks(self, task_id: int) -> list[TimeBlock]:
        ...

    def get_task_reminders(self, task_id: int) -> list[Reminder]:
        ...

    def get_task_attachments(self, task_id: int) -> list[Attachment]:
        ...

    def remove_task(self, task: Task) -> None:
        ...

    

    

    
    