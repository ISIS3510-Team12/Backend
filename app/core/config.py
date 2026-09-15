from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache
from pydantic import BaseModel

Environment = Literal["dev", "prod"]

class EnvironmentConfig(BaseModel):
    env: Environment

class CoreSettings(BaseSettings):
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
    ENV: str = "dev"

    model_config = SettingsConfigDict(
        env_file=".env.dev",
    )


class ProdSettings(CoreSettings):
    ENV: str = "prod"

    model_config = SettingsConfigDict(
        env_file=".env.prod",
    )


@lru_cache
def get_settings(env: Environment) -> CoreSettings:
    config = EnvironmentConfig(env=env)

    if config.env == "dev":
        return DevSettings()

    return ProdSettings()

settings = get_settings(env="dev")
