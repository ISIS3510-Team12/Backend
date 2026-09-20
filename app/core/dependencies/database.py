from sqlmodel import  create_engine, Session
from app.core.config import settings
from typing import Annotated
from fastapi import Depends
from typing import Generator

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

