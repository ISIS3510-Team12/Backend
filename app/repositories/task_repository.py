from . import BaseRepository
from app.models import Task, User, TimeBlock, Reminder, Attachment, TaskEvent
from sqlmodel import select

class TaskRepository(BaseRepository):

    def save(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def save_time_block_to_task(self, time_block: TimeBlock) -> TimeBlock:
        ...

    def save_reminder_to_task(self, reminder: Reminder) -> Reminder:
        ...

    def save_attachment_to_task(self, attachment: Attachment) -> Attachment:
        ...

    def save_task_event(self, task_event: TaskEvent) -> TaskEvent:
        ...
    
    def get_task_by_user_id(self, user_id: str, task_id: int) -> Task | None:
        ...

    def get_task_time_blocks(self, task_id: int) -> list[TimeBlock] | None:
        ...

    def get_task_reminders(self, task_id: int) -> list[Reminder] | None:
        ...

    def get_task_attachments(self, task_id: int) -> list[Attachment] | None:
        ...

    def get_task_events(self, task_id: int) -> list[TaskEvent] | None:
        ...

    def remove(self, task: Task) -> None:
        ...
        