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
    if "updated_at" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE companies ADD COLUMN updated_at TIMESTAMP"))
            connection.execute(
                text("UPDATE companies SET updated_at = created_at WHERE updated_at IS NULL")
            )

    new_text_columns = {
        "address": "VARCHAR(512)",
        "website": "VARCHAR(512)",
        "phone": "VARCHAR(64)",
        "email": "VARCHAR(256)",
    }
    for column_name, column_type in new_text_columns.items():
        if column_name not in column_names:
            with engine.begin() as connection:
                connection.execute(text(f"ALTER TABLE companies ADD COLUMN {column_name} {column_type}"))

    if "bot_logs" in inspector.get_table_names():
        bot_log_columns = {column["name"] for column in inspector.get_columns("bot_logs")}
        if "search_history_id" not in bot_log_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE bot_logs ADD COLUMN search_history_id INTEGER"))
        if "updated_at" not in bot_log_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE bot_logs ADD COLUMN updated_at TIMESTAMP"))
                connection.execute(
                    text("UPDATE bot_logs SET updated_at = created_at WHERE updated_at IS NULL")
                )
        # Eski/derlenmemis Delphi istemciler token gondermeden tarama tetikleyebiliyor;
        # bu durumda user_id bilinmez, bu yuzden zorunlu olmaktan cikarildi.
        user_id_column = next(
            (column for column in inspector.get_columns("bot_logs") if column["name"] == "user_id"), None
        )
        if user_id_column is not None and not user_id_column["nullable"]:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE bot_logs ALTER COLUMN user_id DROP NOT NULL"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
