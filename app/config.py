from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SQLALCHEMY_URL: str
    SECRET_KEY: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"  # automatically loads from .env


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
