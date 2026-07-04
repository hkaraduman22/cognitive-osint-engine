from fastapi import APIRouter, status

from app.schemas.schemas import ScraperTriggerRequest

router = APIRouter()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_scraper(request: ScraperTriggerRequest):
    # Asenkron tetikleme işlemi burada service katmanında yazılacak
    # Accepts JSON: {"target_domain": "...", "keyword": "..."}
    return {"message": "Scraper tetiklendi, işlem başlatıldı"}
