import os
import sqlite3
from pathlib import Path
from typing import Optional


DEFAULT_QUEUE_NAME = "osint_raw_queue"
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "osint_queue.db"


class SQLiteMessageQueue:
    """Ayrı süreçlerin ortak kullanabildiği kalıcı ve atomik SQLite kuyruğu."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        configured_path = db_path or os.getenv("OSINT_QUEUE_DB") or DEFAULT_DB_PATH
        self.db_path = Path(configured_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=10000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS queue_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    queue_name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS ix_queue_messages_name_id "
                "ON queue_messages(queue_name, id)"
            )

    def push(self, queue_name: str, payload: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO queue_messages(queue_name, payload) VALUES (?, ?)",
                (queue_name, payload),
            )

    def pop(self, queue_name: str) -> Optional[str]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT id, payload FROM queue_messages "
                "WHERE queue_name = ? ORDER BY id LIMIT 1",
                (queue_name,),
            ).fetchone()
            if row is None:
                connection.commit()
                return None

            connection.execute("DELETE FROM queue_messages WHERE id = ?", (row[0],))
            connection.commit()
            return str(row[1])
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_all(self, queue_name: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM queue_messages "
                "WHERE queue_name = ? ORDER BY id",
                (queue_name,),
            ).fetchall()
        return [str(row[0]) for row in rows]
