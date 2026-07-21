from typing import Optional

from fastapi import APIRouter, Query, status

from app.schemas.schemas import PersonnelCreate, PersonnelResponse

router = APIRouter()


@router.post("/personnel", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
def create_personnel(personnel: PersonnelCreate):
    # Bot tarafından gönderilen personel verileri service katmanında işlenecek
    return {
        "id": 0,
        "first_name": personnel.first_name,
        "last_name": personnel.last_name,
        "title": personnel.title,
        "email": personnel.email,
        "company_id": personnel.company_id,
        "confidence_score": personnel.confidence_score,
        "created_at": "1970-01-01T00:00:00Z",
    }


from app.schemas.schemas import PersonnelCreate, PersonnelResponse, SearchHistoryResponse


@router.post("/personnel", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
def create_personnel(personnel: PersonnelCreate):
    # Bot tarafından gönderilen personel verileri service katmanında işlenecek
    return {
        "id": 0,
        "first_name": personnel.first_name,
        "last_name": personnel.last_name,
        "title": personnel.title,
        "email": personnel.email,
        "company_id": personnel.company_id,
        "confidence_score": personnel.confidence_score,
        "created_at": "1970-01-01T00:00:00Z",
    }


@router.get("/search-history", response_model=list[SearchHistoryResponse])
def list_search_history(user_id: Optional[int] = Query(None)):
    # Bu endpoint henüz service katmanına bağlanmadı; gerçek dönüşler ileride eklenecek
    return []