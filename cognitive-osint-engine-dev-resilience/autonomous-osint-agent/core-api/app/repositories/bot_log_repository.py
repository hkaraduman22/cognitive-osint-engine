from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import BotLog


class BotLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: int | None, query: str, status: str, search_history_id: int | None = None
    ) -> BotLog:
        log = BotLog(user_id=user_id, query=query, status=status, search_history_id=search_history_id)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update_status(self, log_id: int, status: str, message: str | None = None) -> None:
        log = self.db.get(BotLog, log_id)
        if log is not None:
            log.status = status
            if message is not None:
                log.message = message
            self.db.commit()

    def get_latest_by_search_history_id(self, search_history_id: int) -> BotLog | None:
        return self.db.scalar(
            select(BotLog)
            .where(BotLog.search_history_id == search_history_id)
            .order_by(BotLog.id.desc())
        )
