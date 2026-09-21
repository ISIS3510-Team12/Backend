from . import BaseRepository
from app.models import Task, User, TimeBlock, Reminder, Attachment, TaskEvent
from sqlmodel import select
from app.exceptions import TaskNotFoundException, TaskObjectNotSupportedException

class TaskRepository(BaseRepository):

    def save(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def _add_related_task_object(self, task: Task, obj: object) -> None:
        if isinstance(obj, TimeBlock):
            task.time_blocks.append(obj)
        elif isinstance(obj, Reminder):
            task.reminders.append(obj)
        elif isinstance(obj, Attachment):
            task.attachments.append(obj)
        elif isinstance(obj, TaskEvent):
                task.events.append(obj)   
        else:
            raise TaskObjectNotSupportedException(type(obj).__name__)

    def _save_object_to_task(self, task_id: str, obj) -> None:
        task = self.db.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)
        self._add_related_task_object(task, obj)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

    def save_time_block_to_task(self, task_id: str, time_block: TimeBlock) -> TimeBlock:
        self._save_object_to_task(task_id, time_block)
        return time_block

    def save_reminder_to_task(self, task_id: str, reminder: Reminder) -> Reminder:
        self._save_object_to_task(task_id, reminder)
        return reminder

    def save_attachment_to_task(self, task_id: str, attachment: Attachment) -> Attachment:
        self._save_object_to_task(task_id, attachment)
        return attachment

    def save_event_to_task(self, task_id: str, event: TaskEvent) -> TaskEvent:
        self._save_object_to_task(task_id, event)
        return event

    def get_task_by_user_id(self, user_id: str, task_id: str) -> Task | None:
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = self.db.exec(query).first()
        return result
        
    def get_tasks_by_user_id(self, user_id: str) -> list[Task] | None:
        user = self.db.get(User, user_id)
        if user:
            return user.tasks
        return None
    
    


    

    