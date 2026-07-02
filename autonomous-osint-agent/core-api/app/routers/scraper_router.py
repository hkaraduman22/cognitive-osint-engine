from fastapi import APIRouter, status

from app.schemas.schemas import SearchHistoryCreate

router = APIRouter()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_scraper(request: SearchHistoryCreate):
    # Asenkron tetikleme işlemi burada service katmanında yazılacak
    return {"message": "Scraper tetiklendi, işlem başlatıldı"}
