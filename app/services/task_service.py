from app.models import Task, TimeBlock, Reminder, Attachment, TaskEvent
from app.repositories.task_repository import TaskRepository
from app.exceptions import TaskExistsException, TaskNotFoundException

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, user_id:str ,task: Task) -> Task:
        ...

    

    

    

    
    