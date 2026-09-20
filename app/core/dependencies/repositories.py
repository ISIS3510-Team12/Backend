from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import DatabaseSession
from app.repositories.user_repository import UserRepository

def get_user_repository(db: DatabaseSession) -> UserRepository:
    return UserRepository(db)

UserRepositoryDep = Annotated[
    UserRepository,
    Depends(get_user_repository),
]