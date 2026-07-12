from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.company import SearchHistoryCompany
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

    def list_records(self, user_id: int, min_score: int = 85) -> list[Record]:
        stmt = (
            select(Record)
            .where(Record.created_by == user_id, Record.score >= min_score)
            .order_by(Record.created_at.desc())
        )
        return self.db.scalars(stmt).all()

    def save_bot_log(self, user_id: int, query: str, status: str, message: str | None = None) -> BotLog:
        bot_log = BotLog(user_id=user_id, query=query, status=status, message=message)
        self.db.add(bot_log)
        self.db.commit()
        self.db.refresh(bot_log)
        return bot_log

    def link_search_history_company(self, search_history_id: int, company_id: int, confidence_score: int) -> SearchHistoryCompany:
        stmt = select(SearchHistoryCompany).where(
            SearchHistoryCompany.search_history_id == search_history_id,
            SearchHistoryCompany.company_id == company_id,
        )
        existing = self.db.scalars(stmt).first()
        if existing:
            existing.confidence_score = confidence_score
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        link = SearchHistoryCompany(
            search_history_id=search_history_id,
            company_id=company_id,
            confidence_score=confidence_score,
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def list_bot_logs(self) -> list[BotLog]:
        return self.db.scalars(select(BotLog).order_by(BotLog.created_at.desc())).all()

    def list_user_search_history_for_admin(self, user_id: int) -> list[dict[str, object]]:
        latest_status_subquery = (
            select(BotLog.status)
            .where(BotLog.search_history_id == SearchHistory.id)
            .order_by(BotLog.created_at.desc(), BotLog.id.desc())
            .limit(1)
            .scalar_subquery()
        )

        company_count_subquery = (
            select(func.count(SearchHistoryCompany.id))
            .where(SearchHistoryCompany.search_history_id == SearchHistory.id)
            .scalar_subquery()
        )

        stmt = (
            select(
                SearchHistory.id.label("search_history_id"),
                SearchHistory.query,
                SearchHistory.created_at,
                latest_status_subquery.label("status"),
                company_count_subquery.label("company_count"),
            )
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
        )

        rows = self.db.execute(stmt).all()
        return [
            {
                "search_history_id": row.search_history_id,
                "query": row.query,
                "created_at": row.created_at,
                "status": row.status or "pending",
                "company_count": int(row.company_count or 0),
            }
            for row in rows
        ]

    def get_search_history_detail_for_admin(self, search_history_id: int) -> dict[str, object] | None:
        latest_status_subquery = (
            select(BotLog.status)
            .where(BotLog.search_history_id == SearchHistory.id)
            .order_by(BotLog.created_at.desc(), BotLog.id.desc())
            .limit(1)
            .scalar_subquery()
        )

        stmt = (
            select(
                SearchHistory.id.label("search_history_id"),
                SearchHistory.query,
                SearchHistory.created_at,
                latest_status_subquery.label("status"),
            )
            .where(SearchHistory.id == search_history_id)
        )

        row = self.db.execute(stmt).one_or_none()
        if row is None:
            return None

        return {
            "search_history_id": row.search_history_id,
            "query": row.query,
            "created_at": row.created_at,
            "status": row.status or "pending",
        }
