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
        self.db.add(time_block)
        self.db.commit()
        self.db.refresh(time_block)
        return time_block

    def save_reminder_to_task(self, reminder: Reminder) -> Reminder:
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def save_attachment_to_task(self, attachment: Attachment) -> Attachment:
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def save_task_event(self, task_event: TaskEvent) -> TaskEvent:
        self.db.add(task_event)
        self.db.commit()
        self.db.refresh(task_event)
        return task_event
    
    def get_task_by_user_id(self, user_id: str, task_id: int) -> Task | None:
        task = self.db.get(Task, task_id)
        if task and task.user_id == user_id:
            return task
        return None

    def get_task_time_blocks(self, task_id: int) -> list[TimeBlock] | None:
        task = self.db.get(Task, task_id)
        if task:
            return task.time_blocks
        return None

    def get_task_reminders(self, task_id: int) -> list[Reminder] | None:
        task = self.db.get(Task, task_id)
        if task:
            return task.reminders
        return None

    def get_task_attachments(self, task_id: int) -> list[Attachment] | None:
        task = self.db.get(Task, task_id)
        if task:
            return task.attachments
        return None

    def get_task_events(self, task_id: int) -> list[TaskEvent] | None:
        task = self.db.get(Task, task_id)
        if task:
            return task.events
        return None

    def remove(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
        