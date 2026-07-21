from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import BotLog, Record, SearchHistory


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_search_history(self, user_id: int, query: str) -> SearchHistory:
        search = SearchHistory(user_id=user_id, query=query)
        self.db.add(search)
        self.db.commit()
        self.db.refresh(search)
        return search

    def get_last_searches(self, user_id: int, limit: int = 7) -> list[SearchHistory]:
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id).order_by(SearchHistory.created_at.desc()).limit(limit)
        return self.db.scalars(stmt).all()

    def save_record(self, title: str, content: str, source: str | None, score: int, created_by: int) -> Record:
        record = Record(title=title, content=content, source=source, score=score, created_by=created_by)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_records(self) -> list[Record]:
        return self.db.scalars(select(Record).order_by(Record.created_at.desc())).all()

    def save_bot_log(self, user_id: int, query: str, status: str, message: str | None = None) -> BotLog:
        bot_log = BotLog(user_id=user_id, query=query, status=status, message=message)
        self.db.add(bot_log)
        self.db.commit()
        self.db.refresh(bot_log)
        return bot_log

    def list_bot_logs(self) -> list[BotLog]:
        return self.db.scalars(select(BotLog).order_by(BotLog.created_at.desc())).all()