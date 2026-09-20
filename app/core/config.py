from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache
from pathlib import Path
import os
import json

BASE_DIR = Path(__file__).resolve().parent

Environment = Literal["dev", "prod"]

class FirebaseCredentials(BaseSettings):
    type: str = ""
    project_id: str = ""
    private_key_id: str = ""
    private_key: str = ""
    client_email: str = ""
    client_id: str = ""
    auth_uri: str = ""
    token_uri: str = ""
    auth_provider_x509_cert_url: str = ""
    client_x509_cert_url: str = ""
    universe_domain: str = ""

    model_config = SettingsConfigDict(
        env_prefix="FIREBASE_",
        extra="ignore",
    )

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

    @property
    def FIREBASE_CREDENTIALS_DATA(self) -> FirebaseCredentials:
        return FirebaseCredentials()

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DevSettings(CoreSettings):
    """
    Development settings for the application.
    """
    ENV: Environment = "dev"

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProdSettings(CoreSettings):
    """
    Production settings for the application.
    """
    ENV: Environment = "prod"

    model_config = SettingsConfigDict(
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> CoreSettings:
    env = os.getenv("ENV", "dev")

    if env == "prod":
        return ProdSettings()

    return DevSettings()


settings = get_settings()
