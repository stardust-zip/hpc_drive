from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./drive.db"

    AUTH_SERVICE_ME_URL: str = "http://localhost:8080/api/v1/me"

    class Config:
        env_file = ".env"


settings = Settings()
