from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


def _normalize_postgres_url(url: str, async_mode: bool) -> str:
    if not url:
        return url

    normalized = str(url).strip()
    if normalized.startswith("postgres://"):
        normalized = "postgresql://" + normalized[len("postgres://"):]

    if async_mode:
        if normalized.startswith("postgresql+asyncpg://"):
            return normalized
        if normalized.startswith("postgresql://"):
            return normalized.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        if normalized.startswith("postgresql+asyncpg://"):
            return normalized.replace("postgresql+asyncpg://", "postgresql://", 1)

    return normalized


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://animface:animface123@localhost:5432/animface_db"
    SYNC_DATABASE_URL: str = "postgresql://animface:animface123@localhost:5432/animface_db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_UPLOAD_DIR: str = "uploads"
    MAX_VIDEO_SIZE_MB: int = 100
    MAX_VIDEO_DURATION_SECONDS: int = 60

    # AWS (future)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = "animface-videos"
    AWS_REGION: str = "us-east-1"

    # AI Pipeline
    ANIME_MODEL: str = "mock"
    ANIME_WORKER_CONCURRENCY: int = 2

    def model_post_init(self, __context) -> None:
        # Hosting providers often expose postgres:// URLs. Normalize once for both engines.
        async_source = self.DATABASE_URL or self.SYNC_DATABASE_URL
        sync_source = self.SYNC_DATABASE_URL or self.DATABASE_URL
        self.DATABASE_URL = _normalize_postgres_url(async_source, async_mode=True)
        self.SYNC_DATABASE_URL = _normalize_postgres_url(sync_source, async_mode=False)

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def max_video_size_bytes(self) -> int:
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
