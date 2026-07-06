import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "supersecretchangeme")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))


settings = Settings()
