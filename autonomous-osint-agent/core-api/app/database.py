import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def ensure_mvp_schema() -> None:
    """Mevcut MVP veritabanını veri silmeden yeni zorunlu kolonlarla uyumlar."""
    inspector = inspect(engine)
    if "companies" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("companies")}
    if "source_url" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE companies ADD COLUMN source_url VARCHAR(1024)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
