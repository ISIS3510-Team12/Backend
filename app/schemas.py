from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    major: str

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    major: str | None = None
    email: str | None = None

class UserPreferencesUpdate(BaseModel):
    push_enabled: bool | None = None