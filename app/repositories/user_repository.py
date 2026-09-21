from . import BaseRepository
from app.models import User, UserPreferences, Group, Task
from sqlmodel import select

class UserRepository(BaseRepository):

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save_preferences_to_user(self, preferences: UserPreferences) -> UserPreferences:
        self.db.add(preferences)
        self.db.commit()
        self.db.refresh(preferences)
        return preferences
    
    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.get(User, email)

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
        
    def remove(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
