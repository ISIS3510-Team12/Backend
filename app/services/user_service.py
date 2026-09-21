from app.repositories.user_repository import UserRepository
from app.models import User, UserPreferences
from app.exceptions import UserNotFoundException
from app.schemas import UserUpdate, UserPreferencesUpdate

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user: User) -> User:
        return self.repository.save(user)

    def create_user_preferences(self, user_id:str, preferences: UserPreferences) -> UserPreferences:
        return self.repository.save_preferences_to_user(user_id, preferences)

    def update_user(self, user_id: str, user: UserUpdate) -> None:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        user_data = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        self.repository.save(db_user)

    def update_user_preferences(self, user_id: str, preferences: UserPreferencesUpdate) -> None:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        db_preferences = db_user.preferences
        preferences_data = preferences.model_dump(exclude_unset=True)
        db_preferences.sqlmodel_update(preferences_data)
        self.repository.save_preferences_to_user(db_user.user_id, db_preferences)
        
    def get_user_by_id(self, user_id: str) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        return self.repository.get_by_email(email)

    def get_user_preferences_by_user_id(self, user_id: str) -> UserPreferences | None:
        return self.repository.get_user_preferences(user_id)

    def delete_user(self, user: User) -> None:
        self.repository.remove(user)

    def get_auth_provider(self, firebase_user: dict) -> str:
        firebase_claims = firebase_user.get("firebase")
        if not isinstance(firebase_claims, dict):
            return "firebase"
        sign_in_provider = firebase_claims.get("sign_in_provider")
        if isinstance(sign_in_provider, str) and sign_in_provider:
            return sign_in_provider
        return "firebase"