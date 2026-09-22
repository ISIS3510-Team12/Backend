from . import BaseRepository
from app.models import Task, User, TimeBlock, Reminder, Attachment, TaskEvent
from sqlmodel import select

class TaskRepository(BaseRepository):
    def get_task_by_user_id(self, task_id: int, user_id: int) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id, 
            Task.user_id == user_id
        )
        return self.db.exec(statement).first()

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