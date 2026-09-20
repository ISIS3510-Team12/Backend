from typing import Annotated
from fastapi import Depends
from app.core.dependencies.repositories import UserRepositoryDep
from app.services.user_service import UserService

def get_user_service(repo: UserRepositoryDep) -> UserService:
    return UserService(repo)

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]



