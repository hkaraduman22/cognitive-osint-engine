from typing import Optional

from fastapi import APIRouter, Query, status

from app.schemas.schemas import CompanyCreate, CompanyResponse

router = APIRouter()


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate):
    # Bot tarafından gönderilen şirket verileri service katmanında işlenecek
    return {
        "id": 0,
        "name": company.name,
        "website": company.website,
        "location": company.location,
        "description": company.description,
        "source": company.source,
        "confidence_score": company.confidence_score,
        "created_at": "1970-01-01T00:00:00Z",
    }


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(location: Optional[str] = Query(None), source: Optional[str] = Query(None)):
    # Şirket listesi filtreleri, service katmanında uygulanacak
    return []
