from typing import Generic, TypeVar
from sqlmodel import Session, SQLModel


ModelT = TypeVar("ModelT", bound=SQLModel)

class BaseRepository(Generic[ModelT]):
    """
    Base repository class that provides common database operations for SQLModel models.
    """
    def __init__(self, db: Session):
        self.db = db
