class BaseException(Exception):
    """
    Base class for all custom exceptions in the application.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserNotFoundException(BaseException):
    """
    Exception raised when a user is not found in the database.
    """
    def __init__(self, user_id: str):
        message = f"User with ID '{user_id}' not found."
        super().__init__(message)

class TaskNotFoundException(BaseException):
    """
    Exception raised when a task is not found in the database.
    """
    def __init__(self, task_id: str):
        message = f"Task with ID '{task_id}' not found."
        super().__init__(message)

class TaskObjectNotSupportedException(BaseException):
    """
    Exception raised when an unsupported object type is attempted to be saved to a task.
    """
    def __init__(self, object_type: str):
        message = f"Object type '{object_type}' is not supported for saving to a task."
        super().__init__(message)   


class UserEmailNotFoundException(BaseException):
    """
    Exception raised when a user with a specific email is not found in the database.
    """
    def __init__(self, email: str):
        message = f"User with email '{email}' not found."
        super().__init__(message)