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