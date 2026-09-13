from sqlmodel import SQLModel, create_engine, Session
import os

postgres_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")
engine = create_engine(postgres_url, echo=True)

def get_db() -> Session:
    with Session(engine) as session:
        yield session

        