from sqlmodel import SQLModel, create_engine, Session
import os
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_db() -> Session:
    with Session(engine) as session:
        yield session

        