import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


CORE_API_PATH = Path(__file__).resolve().parents[1] / "autonomous-osint-agent" / "core-api"
if str(CORE_API_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_API_PATH))

from app.models import Base
from app.models.company import Company
from app.schemas.company_schema import CompanyCreate
from app.services.company_service import create_elite_company


def _session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_duplicate_company_is_merged_without_losing_quality() -> None:
    with _session() as db:
        first = create_elite_company(
            db,
            CompanyCreate(
                name="İstanbul CNC Makine",
                industry="CNC freze üretimi",
                city="İstanbul",
                source_url="https://example.com/first",
                confidence_score=95,
            ),
        )
        duplicate = create_elite_company(
            db,
            CompanyCreate(
                name="  istanbul   cnc makine ",
                industry=None,
                city="istanbul",
                source_url=None,
                confidence_score=85,
            ),
        )

        assert duplicate.id == first.id
        assert db.scalar(select(func.count()).select_from(Company)) == 1
        assert duplicate.industry == "CNC freze üretimi"
        assert duplicate.source_url == "https://example.com/first"
        assert duplicate.confidence_score == 95
        assert duplicate.updated_at is not None


def test_invalid_source_url_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Kaynak URL"):
        CompanyCreate(
            name="Geçersiz Kaynaklı Firma",
            source_url="javascript:alert(1)",
            confidence_score=90,
        )
