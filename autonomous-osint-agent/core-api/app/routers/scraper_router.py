from fastapi import APIRouter, status, BackgroundTasks

from app.schemas.schemas import ScraperTriggerRequest
from app.services.search_service import run_scraper_background

router = APIRouter()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_scraper(request: ScraperTriggerRequest, background_tasks: BackgroundTasks):
    """Trigger the scraper pipeline asynchronously.

    The endpoint accepts JSON: {"target_domain": "...", "keyword": "..."}
    and starts the scraping + LLM pipeline in the background.
    """
    background_tasks.add_task(run_scraper_background, request.target_domain, request.keyword)
    return {"message": "Scraper tetiklendi, arka planda işlem başlatıldı"}
