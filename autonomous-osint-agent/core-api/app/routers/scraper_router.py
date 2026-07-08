from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db

# İçe aktarma hatasını düzelten yeni import satırı
from app.services.search_service import SearchService, run_scraper_background

router = APIRouter()

@router.post("/trigger")
async def trigger_scraper(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Arayüzden gelen JSON datasındaki hedef kelimeyi/domaini al
    target = data.get("target_domain", data.get("query", "Bilinmeyen Hedef"))
    
    # Botu arka planda çalıştır, API'yi bekletme
    background_tasks.add_task(run_scraper_background, target, db)
    
    return {
        "status": "success", 
        "message": f"Bot {target} için başarıyla tetiklendi ve kuyruğa alındı."
    }