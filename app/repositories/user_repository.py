from . import BaseRepository
from app.models import User, UserPreferences, Group, Task
from sqlmodel import select

class UserRepository(BaseRepository):
    """
    UserRepository class that provides database operations for retrieving Users data.
    """
    
    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_user_preferences(self, user_id: str) -> UserPreferences | None:
        user = self.db.get(User, user_id)
        if user:
            return user.preferences
        return None

    def get_user_groups(self, user_id: str) -> list[Group] | None:
        user = self.db.get(User, user_id)
        if user:
            return user.groups
        return None

    def get_user_tasks(self, user_id: str) -> list[Task] | None:
        user = self.db.get(User, user_id)
        if user:
            return user.tasks
        return None
        