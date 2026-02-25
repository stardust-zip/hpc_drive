import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/hpc_drive"
    
    JWT_SECRET: str = "vananhdeptraiokokokokokokokokokokokokokokok"
    JWT_ALGORITHM: str = "HS256"

    LEARNING_SERVICE_URL: str = os.getenv(
        "LEARNING_SERVICE_URL", "http://localhost:8000"
    )

    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file: str = ".env"

    @property
    def UPLOADS_DIR(self) -> Path:
        return Path(__file__).resolve().parent / self.UPLOAD_DIR

settings = Settings()
