from fastapi import HTTPException

class BaseHTTPException(HTTPException):
    """
    Base class for all custom HTTP exceptions in the application.
    """
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)

class UserNotFoundException(BaseHTTPException):
    """
    Exception raised when a user is not found in the database.
    """
    def __init__(self, user_id: str):
        message = f"User with ID {user_id} not found."
        super().__init__(status_code=404, message=message)

class UserExistsException(BaseHTTPException):
    """
    Exception raised when a user already exists in the database.
    """
    def __init__(self, user_id: str):
        message = f"User with ID {user_id} already exists."
        super().__init__(status_code=400, message=message)

class UserPreferencesNotFoundException(BaseHTTPException):
    """
    Exception raised when user preferences are not found in the database.
    """
    def __init__(self, user_id: str):
        message = f"User preferences for user ID {user_id} not found."
        super().__init__(status_code=404, message=message)

class FirebaseUserUIDMissingException(BaseHTTPException):
    """
    Exception raised when a Firebase user does not have a UID.
    """
    def __init__(self):
        message = "Firebase user must have a UID."
        super().__init__(status_code=400, message=message)

class TaskExistsException(BaseHTTPException):
    """
    Exception raised when a task already exists for a user.
    """
    def __init__(self, task_id: int):
        message = f"Task with ID {task_id} already exists for this user."
        super().__init__(status_code=400, message=message)

class TaskNotFoundException(BaseHTTPException):
    """
    Exception raised when a task is not found in the database.
    """
    def __init__(self, task_id: str):
        message = f"Task with ID {task_id} not found."
        super().__init__(status_code=404, message=message)

class TaskObjectNotSupportedException(BaseHTTPException):
    """
    Exception raised when an unsupported object type is added to a task.
    """
    def __init__(self, object_type: str):
        message = f"Object of type {object_type} is not supported for tasks."
        super().__init__(status_code=400, message=message)
    
class ProjectNotFoundException(BaseHTTPException):
    """
    Exception raised when a project is not found in the database.
    """
    def __init__(self, project_id: int):
        message = f"Project with ID {project_id} not found."
        super().__init__(status_code=404, message=message)