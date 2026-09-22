from app.core.consts import STATUS_NOT_STARTED
from app.models import Task, TimeBlock, Reminder, Attachment, TaskEvent
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.exceptions import ProjectNotFoundException, TaskExistsException, TaskNotFoundException
from app.schemas import TaskCreate, TaskUpdate

class TaskService:
    def __init__(
        self, 
        repository: TaskRepository,
        project_repository: ProjectRepository
    ):
        self.repository = repository
        self.project_repository = project_repository

    def create_task(self, user_id: int ,data: TaskCreate) -> Task:
        project = self.project_repository.get_project_by_id(data.project_id) if data.project_id else None
        
        if project is None and data.project_id is not None:
            raise ProjectNotFoundException(data.project_id)
        
        task = Task(
            title=data.title,
            task_type=data.task_type,
            status=STATUS_NOT_STARTED,
            is_priority=data.is_priority,
            deadline=data.deadline,
            user_id=user_id,
            project_id=data.project_id
        )
        
        return self.repository.create_task(task)

    def get_tasks_by_user(self, user_id: int) -> list[Task]:
        return self.repository.get_all_tasks_by_user(user_id)
    
    def get_task_by_user(self, task_id: int, user_id: int) -> Task:
        task = self.repository.get_task_by_user_id(task_id, user_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return task
    
    def get_tasks_by_project(self, task_id: int, project_id: int) -> list[Task]:
        project = self.project_repository.get_project_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(project_id)
        
        return self.repository.get_all_tasks_by_project(project_id)
    
    def get_task_by_project(self, task_id: int, project_id: int) -> Task:
        project = self.project_repository.get_project_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(project_id)
        task = self.repository.get_task_by_project(project_id)
        if task is None:
            raise TaskNotFoundException(task_id)
        return task
    
    def update_task(self, task_id: int, user_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id, user_id)
        
        if data.project_id is not None:
            project = self.project_repository.get_project_by_id(data.project_id)
            if project is None:
                raise ProjectNotFoundException(data.project_id)
        
        return self.repository.update_task(task, data)

    def delete_task(self, task_id: int, user_id: int) -> None:
        task = self.get_task(task_id, user_id)
        self.repository.delete_task(task)