from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./drive.db"

    AUTH_SERVICE_ME_URL: str = "http://localhost:8082/api/v1/me"

    class Config:
        env_file: str = ".env"

    UPLOADS_DIR: Path = Path(__file__).resolve().parent / "uploads"


settings = Settings()
