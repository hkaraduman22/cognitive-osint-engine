# ruff: noqa: E402

import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


CORE_API_PATH = Path(__file__).resolve().parents[1] / "autonomous-osint-agent" / "core-api"
if str(CORE_API_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_API_PATH))

from app.models import Base, SearchHistory, User
from app.schemas.company_schema import CompanyCreate
from app.services.company_service import create_elite_company, get_companies


def test_company_is_linked_to_search_with_source_url() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = User(username="mvp-user", hashed_password="test-hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        search = SearchHistory(user_id=user.id, query="İstanbul CNC freze üreticileri")
        db.add(search)
        db.commit()
        db.refresh(search)

        created = create_elite_company(
            db,
            CompanyCreate(
                name="Örnek CNC Makine",
                industry="CNC freze üretimi",
                city="İstanbul",
                source_url="https://example.com/cnc",
                confidence_score=92,
                search_history_id=search.id,
                officials=[],
            ),
        )

        results = get_companies(
            db,
            search_history_id=search.id,
            current_user={"id": user.id, "is_admin": False},
        )

        assert [company.id for company in results] == [created.id]
        assert results[0].source_url == "https://example.com/cnc"
        assert results[0].confidence_score == 92
