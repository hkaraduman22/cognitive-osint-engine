from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company, CompanyOfficial, SearchHistoryCompany
from app.models.models import SearchHistory
from app.repositories.search_repository import SearchRepository
from app.schemas.company_schema import CompanyCreate


def create_elite_company(db: Session, company_in: CompanyCreate) -> Company:
    search_repository = SearchRepository(db)
    stmt = select(Company).where(Company.name == company_in.name, Company.city == company_in.city)
    existing_company = db.scalars(stmt).first()

    if existing_company:
        existing_company.industry = company_in.industry
        existing_company.source_url = company_in.source_url
        existing_company.confidence_score = company_in.confidence_score

        if company_in.officials is not None:
            existing_company.officials.clear()
            for official_in in company_in.officials:
                existing_company.officials.append(
                    CompanyOfficial(
                        full_name=official_in.full_name,
                        title=official_in.title,
                        linkedin_url=official_in.linkedin_url,
                    )
                )

        db.add(existing_company)
        db.commit()
        db.refresh(existing_company)
        if company_in.search_history_id is not None:
            search_repository.link_search_history_company(
                search_history_id=company_in.search_history_id,
                company_id=existing_company.id,
                confidence_score=company_in.confidence_score,
            )
        return existing_company

    company = Company(
        name=company_in.name,
        industry=company_in.industry,
        city=company_in.city,
        source_url=company_in.source_url,
        confidence_score=company_in.confidence_score,
    )

    if company_in.officials:
        for official_in in company_in.officials:
            company.officials.append(
                CompanyOfficial(
                    full_name=official_in.full_name,
                    title=official_in.title,
                    linkedin_url=official_in.linkedin_url,
                )
            )

    db.add(company)
    db.commit()
    db.refresh(company)
    if company_in.search_history_id is not None:
        search_repository.link_search_history_company(
            search_history_id=company_in.search_history_id,
            company_id=company.id,
            confidence_score=company_in.confidence_score,
        )
    return company


def get_companies(
    db: Session,
    city: str | None = None,
    industry: str | None = None,
    min_confidence: int = 85,
    limit: int = 50,
    skip: int = 0,
    search_history_id: int | None = None,
    current_user: dict | None = None,
) -> list[Company]:
    query = db.query(Company).options(joinedload(Company.officials))

    is_admin = bool(current_user and current_user.get("is_admin"))
    if not is_admin and current_user is not None:
        filters = [
            SearchHistory.user_id == current_user["id"],
            SearchHistoryCompany.confidence_score >= min_confidence,
        ]
        if search_history_id is not None:
            filters.append(SearchHistoryCompany.search_history_id == search_history_id)
        query = (
            query
            .join(SearchHistoryCompany, SearchHistoryCompany.company_id == Company.id)
            .join(SearchHistory, SearchHistory.id == SearchHistoryCompany.search_history_id)
            .filter(*filters)
            .distinct()
        )

    if city:
        query = query.filter(Company.city.ilike(f"%{city}%"))
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))

    if is_admin or current_user is None:
        query = query.filter(Company.confidence_score >= min_confidence)
    return query.offset(skip).limit(limit).all()
