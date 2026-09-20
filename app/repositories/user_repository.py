from . import BaseRepository
from app.models import User, UserPreferences

class UserRepository(BaseRepository):

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save_preferences(self, preferences: UserPreferences) -> UserPreferences:
        self.db.add(preferences)
        self.db.commit()
        self.db.refresh(preferences)
        return preferences

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.get(User, email)

    def get_preferences_by_user_id(self, user_id: str) -> UserPreferences | None:
        return self.db.get(UserPreferences, user_id)

    def remove(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
