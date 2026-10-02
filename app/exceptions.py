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

class GroupNotFoundException(BaseHTTPException):
    def __init__(self, group_id: int):
        message = f"Group with ID {group_id} not found."
        super().__init__(status_code=404, message=message)

class ProjectGroupMismatchException(BaseHTTPException):
    def __init__(self, project_id: int, group_id: int):
        message = f"Project with ID {project_id} does not belong to group {group_id}."
        super().__init__(status_code=400, message=message)

class UserEmailNotFoundException(BaseHTTPException):
    def __init__(self, email: str):
        message = f"User with email {email} not found."
        super().__init__(status_code=404, message=message)

class AlreadyGroupMemberException(BaseHTTPException):
    def __init__(self, email: str):
        message = f"User with email {email} is already a member of the group."
        super().__init__(status_code=409, message=message)

class LastGroupMemberException(BaseHTTPException):
    def __init__(self):
        message = "The last member cannot leave the group; delete the group instead."
        super().__init__(status_code=400, message=message)

class ReminderNotFoundException(BaseHTTPException):
    """
    Exception raised when a reminder is not found for a task.
    """
    def __init__(self, reminder_id: int):
        message = f"Reminder with ID {reminder_id} not found."
        super().__init__(status_code=404, message=message)

class TimeBlockNotFoundException(BaseHTTPException):
    """
    Exception raised when a time block is not found for a task.
    """
    def __init__(self, time_block_id: int):
        message = f"Time block with ID {time_block_id} not found."
        super().__init__(status_code=404, message=message)

class UserLocationNotFoundException(BaseHTTPException):
    """
    Exception raised when a user has no saved location.
    """
    def __init__(self, user_id: str):
        message = f"User with ID {user_id} has no saved location."
        super().__init__(status_code=404, message=message)
