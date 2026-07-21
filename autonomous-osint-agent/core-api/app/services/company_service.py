from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company, CompanyOfficial
from app.schemas.company_schema import CompanyCreate


def create_elite_company(db: Session, company_in: CompanyCreate) -> Company:
    stmt = select(Company).where(Company.name == company_in.name, Company.city == company_in.city)
    existing_company = db.scalars(stmt).first()

    if existing_company:
        existing_company.industry = company_in.industry
        existing_company.sub_industry = company_in.sub_industry
        existing_company.field_of_activity = company_in.field_of_activity
        existing_company.company_size = company_in.company_size
        existing_company.country = company_in.country
        existing_company.website = company_in.website
        existing_company.phone = company_in.phone
        existing_company.email = company_in.email
        existing_company.address = company_in.address
        existing_company.map_location = company_in.map_location
        existing_company.foundation_year = company_in.foundation_year
        existing_company.source = company_in.source
        existing_company.description = company_in.description
        existing_company.confidence_score = company_in.confidence_score

        if company_in.officials is not None:
            existing_company.officials.clear()
            for official_in in company_in.officials:
                existing_company.officials.append(
                    CompanyOfficial(
                        full_name=official_in.full_name,
                        title=official_in.title,
                        field_of_work=official_in.field_of_work,
                        city=official_in.city,
                        country=official_in.country,
                        email=official_in.email,
                        phone=official_in.phone,
                        linkedin_url=official_in.linkedin_url,
                        confidence_score=official_in.confidence_score,
                    )
                )

        db.add(existing_company)
        db.commit()
        db.refresh(existing_company)
        return existing_company

    company = Company(
        name=company_in.name,
        industry=company_in.industry,
        sub_industry=company_in.sub_industry,
        field_of_activity=company_in.field_of_activity,
        company_size=company_in.company_size,
        country=company_in.country,
        city=company_in.city,
        website=company_in.website,
        phone=company_in.phone,
        email=company_in.email,
        address=company_in.address,
        map_location=company_in.map_location,
        foundation_year=company_in.foundation_year,
        source=company_in.source,
        description=company_in.description,
        confidence_score=company_in.confidence_score,
    )

    if company_in.officials:
        for official_in in company_in.officials:
            company.officials.append(
                CompanyOfficial(
                    full_name=official_in.full_name,
                    title=official_in.title,
                    field_of_work=official_in.field_of_work,
                    city=official_in.city,
                    country=official_in.country,
                    email=official_in.email,
                    phone=official_in.phone,
                    linkedin_url=official_in.linkedin_url,
                    confidence_score=official_in.confidence_score,
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
