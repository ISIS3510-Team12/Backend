from . import BaseRepository
from app.models import User, UserPreferences

class UserRepository(BaseRepository):

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.get(User, email)

    def remove(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
