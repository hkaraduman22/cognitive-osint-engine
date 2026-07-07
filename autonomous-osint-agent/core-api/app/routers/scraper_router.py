from fastapi import APIRouter, status, BackgroundTasks, Query
from typing import Dict
from app.services.search_service import run_scraper_background

router = APIRouter()


@router.post("/scan", status_code=status.HTTP_202_ACCEPTED)
def trigger_scraper(background_tasks: BackgroundTasks, query: str = Query(..., alias="query")) -> Dict[str, str]:
    """
    Delphi arayüzündeki butondan gelen istekleri karşılayan uç nokta (endpoint).
    Gelen sorguyu alır ve arka planda çalışan örümcek botları tetikler.
    """
    # Kazıcı fonksiyonunun arka plan görevi (Background Task) olarak kaydedilmesi
    background_tasks.add_task(run_scraper_background, target_domain="", keyword=query)

    return {"message": f"Scraper tetiklendi, arka planda işlem başlatıldı (Sorgu: {query})"}