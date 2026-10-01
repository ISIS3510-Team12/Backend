from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache
import os
from sqlalchemy.engine import URL

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
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore",
    )

class CoreSettings(BaseSettings):
    ENV: Environment = "dev"
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_PASSWORD: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_DB: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = "files"
    S3_REGION: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_AUTH_EMULATOR_HOST: str = ""
    DATABASE_URL: str | None = None

    @property
    def sqlalchemy_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg2://", 1
            )

        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    @property
    def FIREBASE_CREDENTIALS_DATA(self) -> FirebaseCredentials:
        # Real environment variables always win; the file is a local fallback.
        env_file = ".env.prod" if self.ENV == "prod" else ".env.dev"
        return FirebaseCredentials(_env_file=env_file)

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

    Real environment variables always win; ``.env.prod`` is only a local
    convenience for running with ``ENV=prod``.
    """
    ENV: Environment = "prod"

    model_config = SettingsConfigDict(
        env_file=".env.prod",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> CoreSettings:
    env = os.getenv("ENV", "dev")

    if env == "prod":
        return ProdSettings()

    return DevSettings()


settings = get_settings()
