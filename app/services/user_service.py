from app.repositories.user_repository import UserRepository
from app.models import User, UserPreferences
from app.exceptions import UserNotFoundException, UserExistsException, FirebaseUserUIDMissingException, UserPreferencesNotFoundException
from app.schemas import UserUpdate, UserPreferencesUpdate
from botocore.exceptions import ClientError
from app.core.dependencies.external import S3ClientDep

class UserService:
    def __init__(self, repository: UserRepository, s3_client: S3ClientDep):
        self.repository = repository
        self.s3_client = s3_client

    def create_user(self, user: User) -> User:
        if self.repository.get_by_id(user.user_id):
            raise UserExistsException(user.user_id)
        self.repository.db.add(user)
        self.repository.db.commit()
        persisted_user = self.repository.get_by_id(user.user_id)
        if not persisted_user:
            raise UserNotFoundException(user.user_id)
        default_preferences = UserPreferences(user_id=persisted_user.user_id)
        self.repository.db.add(default_preferences)
        self.repository.db.commit()
        self.setup_user_folder_bucket(persisted_user.user_id)
        return persisted_user

    def setup_user_folder_bucket(self, user_id: str) -> None:
        bucket_name = "files"
        file_name = f"attachments/{user_id}/blob.txt"
        body_content = b"Hello, World!"
        try:
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=body_content,
                ContentType="text/plain",
            )
        except ClientError as e:
            print(f"Could not create user folder in bucket '{bucket_name}': {str(e)}")
        
    def update_user(self, user_id: str, user: UserUpdate) -> None:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        user_data = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        self.repository.db.add(db_user)
        self.repository.db.commit()


    def update_user_preferences(self, user_id: str, preferences: UserPreferencesUpdate) -> None:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)

        db_preferences = self.repository.get_user_preferences(db_user.user_id)
        if not db_preferences:
            raise UserPreferencesNotFoundException(user_id)
        
        preferences_data = preferences.model_dump(exclude_unset=True)
        db_preferences.sqlmodel_update(preferences_data)
        self.repository.db.add(db_preferences)
        self.repository.db.commit()
        
    def get_user_by_id(self, user_id: str) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_user_preferences_by_user_id(self, user_id: str) -> UserPreferences | None:
        return self.repository.get_user_preferences(user_id)

    def get_auth_provider(self, firebase_user: dict) -> str:
        firebase_claims = firebase_user.get("firebase")
        if not isinstance(firebase_claims, dict):
            return "firebase"
        sign_in_provider = firebase_claims.get("sign_in_provider")
        if isinstance(sign_in_provider, str) and sign_in_provider:
            return sign_in_provider
        return "firebase"

    def check_user_firebase_uid(self, firebase_user: dict) -> str:
        uid = firebase_user.get("uid")
        if isinstance(uid, str) and uid:
            return uid
        raise FirebaseUserUIDMissingException()

    def delete_user(self, user: User) -> None:
        self.repository.db.delete(user)

    