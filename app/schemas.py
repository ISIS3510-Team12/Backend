from pydantic import BaseModel

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    major: str | None = None
    email: str | None = None