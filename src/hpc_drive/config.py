import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/hpc_drive"
    
    JWT_SECRET: str = "vananhdeptraiokokokokokokokokokokokokokokok"
    JWT_ALGORITHM: str = "HS256"

    AUTH_SERVICE_ME_URL: str = "http://localhost:8082/api/v1/me"  # Fixed: 8082 not 8082
    LEARNING_SERVICE_URL: str = os.getenv(
        "LEARNING_SERVICE_URL", "http://localhost:8000"
    )
    CORS_ALLOWED_ORIGINS: str = os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001,http://127.0.0.1:3000"
    )

    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file: str = ".env"

    @property
    def UPLOADS_DIR(self) -> Path:
        return Path(__file__).resolve().parent / self.UPLOAD_DIR

settings = Settings()