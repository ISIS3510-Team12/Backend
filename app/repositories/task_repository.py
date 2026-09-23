from . import BaseRepository
from app.core.consts import TaskStatus
from app.models import Task, User, TimeBlock, Reminder, Attachment, TaskEvent
from sqlmodel import select

class TaskRepository(BaseRepository):
    def get_task_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def get_task_by_user_id(self, task_id: int, user_id: int) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id, 
            Task.user_id == user_id
        )
        return self.db.exec(statement).first()

    def get_completed_tasks_by_type(
        self,
        user_id: str,
        task_type: str,
        exclude_task_id: int,
    ) -> list[Task]:
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.id != exclude_task_id,
            Task.status == TaskStatus.COMPLETED,
            Task.task_type == task_type,
        )
        results = self.db.exec(statement).all()
        return list(results)

    def get_all_tasks_by_user(self, user_id: int) -> list[Task]:
        statement = select(Task).where(Task.user_id == user_id)
        results = self.db.exec(statement).all()
        return list(results)

    def get_all_tasks_by_project(self, project_id: int) -> list[Task]:
        statement = select(Task).where(Task.project_id == project_id)
        results = self.db.exec(statement)
        return results.all()
    
    def get_task_by_project(self, task_id: int, project_id: int):
        statement = select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id
        )
        return self.db.exec(statement).first()
    
    def create_task(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update_task(self, task: Task, data:dict) -> Task:
        for field, value in data.items():
            setattr(task, field, value)
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete_task(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
    
    def register_task_event(self, task_event: TaskEvent) -> TaskEvent:
        self.db.add(task_event)
        self.db.commit()
        self.db.refresh(task_event)
        return task_event
    
    def get_task_events_by_task_id(self, task_id: int) -> list[TaskEvent]:
        statement = select(TaskEvent).where(TaskEvent.task_id == task_id)
        results = self.db.exec(statement).all()
        return list(results)
    
    def get_task_events_by_user_id(self, user_id: int) -> list[TaskEvent]:
        statement = select(TaskEvent).where(TaskEvent.author_id == user_id)
        results = self.db.exec(statement).all()
        return list(results)