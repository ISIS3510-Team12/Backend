from app.repositories.user_repository import UserRepository
from app.models import User
from app.exceptions import UserNotFoundException
from app.schemas import UserUpdate

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user: User) -> User:
        return self.repository.save(user)

    def update_user(self, user_id: str, user: UserUpdate) -> None:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        user_data = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        self.repository.save(db_user)
        
    def get_user_by_id(self, user_id: str) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        return self.repository.get_by_email(email)

    def delete_user(self, user: User) -> None:
        self.repository.remove(user)