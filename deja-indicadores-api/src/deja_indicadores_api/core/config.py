from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ConfiguraÃ§Ãµes da aplicaÃ§Ã£o carregadas por variÃ¡veis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = Field(
        default="Deja Indicadores API",
        alias="APP_NAME",
    )
    app_env: Literal[
        "development",
        "testing",
        "production",
    ] = Field(
        default="development",
        alias="APP_ENV",
    )
    app_debug: bool = Field(
        default=False,
        alias="APP_DEBUG",
    )
    app_host: str = Field(
        default="127.0.0.1",
        alias="APP_HOST",
    )
    app_port: int = Field(
        default=8000,
        alias="APP_PORT",
    )

    db_host: str = Field(
        default="127.0.0.1",
        alias="DB_HOST",
    )
    db_port: int = Field(
        default=3306,
        alias="DB_PORT",
    )
    db_name: str = Field(
        default="deja_indicadores",
        alias="DB_NAME",
    )
    db_user: str = Field(
        alias="DB_USER",
    )
    db_password: str = Field(
        alias="DB_PASSWORD",
    )
    db_charset: str = Field(
        default="utf8mb4",
        alias="DB_CHARSET",
    )

    jwt_secret_key: str = Field(
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: Literal["HS256"] = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
    )
    access_token_expire_minutes: int = Field(
        default=480,
        gt=0,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    uploads_dir: Path = Field(
        default=Path("uploads"),
        alias="UPLOADS_DIR",
    )

    fotos_face_models_dir: Path = Field(
        default=Path("models/fotos"),
        alias="FOTOS_FACE_MODELS_DIR",
    )

    ticket_attachment_max_size_mb: int = Field(
        default=10,
        gt=0,
        alias="TICKET_ATTACHMENT_MAX_SIZE_MB",
    )

    fotos_media_max_size_mb: int = Field(
        default=500,
        gt=0,
        alias="FOTOS_MEDIA_MAX_SIZE_MB",
    )

    fotos_media_processing_timeout_minutes: int = Field(
        default=60,
        gt=0,
        alias="FOTOS_MEDIA_PROCESSING_TIMEOUT_MINUTES",
    )

    fotos_media_video_conversion_timeout_seconds: int = Field(
        default=3600,
        gt=0,
        alias="FOTOS_MEDIA_VIDEO_CONVERSION_TIMEOUT_SECONDS",
    )

    ffprobe_executable: str = Field(
        default="ffprobe",
        alias="FFPROBE_EXECUTABLE",
    )

    ffmpeg_executable: str = Field(
        default="ffmpeg",
        alias="FFMPEG_EXECUTABLE",
    )

    @property
    def database_url(self) -> str:
        user = quote_plus(
            self.db_user,
        )
        password = quote_plus(
            self.db_password,
        )

        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset={self.db_charset}"
        )


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instÃ¢ncia compartilhada das configuraÃ§Ãµes."""

    return Settings()