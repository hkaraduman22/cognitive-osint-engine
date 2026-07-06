from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company, CompanyOfficial
from app.schemas.company_schema import CompanyCreate


def create_elite_company(db: Session, company_in: CompanyCreate) -> Company:
    stmt = select(Company).where(Company.name == company_in.name, Company.city == company_in.city)
    existing_company = db.scalars(stmt).first()

    if existing_company:
        existing_company.industry = company_in.industry
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
        return existing_company

    company = Company(
        name=company_in.name,
        industry=company_in.industry,
        city=company_in.city,
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
    return company


def get_companies(
    db: Session,
    city: str | None = None,
    industry: str | None = None,
    min_confidence: int = 85,
    limit: int = 50,
    skip: int = 0,
) -> list[Company]:
    query = db.query(Company).options(joinedload(Company.officials))

    if city:
        query = query.filter(Company.city.ilike(f"%{city}%"))
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))

    query = query.filter(Company.confidence_score >= min_confidence)
    return query.offset(skip).limit(limit).all()
