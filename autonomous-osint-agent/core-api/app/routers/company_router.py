from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.company_schema import CompanyCreate, CompanyResponse
from app.services.company_service import create_elite_company, get_companies

router = APIRouter()


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    try:
        company_model = create_elite_company(db, company)
        return company_model
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(
    city: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    min_confidence: int = Query(85, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        companies = get_companies(db, city=city, industry=industry, min_confidence=min_confidence, limit=limit, skip=skip)
        return companies
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
