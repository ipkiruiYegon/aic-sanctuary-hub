from functools import lru_cache
from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"  # automatically loads from .env

@lru_cache
def get_settings():
    return Settings()


settings = get_settings()