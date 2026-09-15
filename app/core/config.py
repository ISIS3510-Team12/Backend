from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache
from pydantic import BaseModel
import os

Environment = Literal["dev", "prod"]

class CoreSettings(BaseSettings):
    ENV: Environment = "dev"
    POSTGRES_HOST: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_DB: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port="5432",
            db=self.POSTGRES_DB,
        )

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DevSettings(CoreSettings):
    ENV: Environment = "dev"

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProdSettings(CoreSettings):
    ENV: Environment = "prod"

    model_config = SettingsConfigDict(
        extra="ignore",
    )


@lru_cache
def get_settings() -> CoreSettings:
    env = os.getenv("ENV", "dev")

    if env == "prod":
        return ProdSettings()

    return DevSettings()


settings = get_settings()
