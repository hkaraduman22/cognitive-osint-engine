import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    jwt_secret: str = "supersecretchangeme"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
