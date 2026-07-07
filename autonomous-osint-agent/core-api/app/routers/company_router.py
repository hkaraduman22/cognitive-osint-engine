import os
import sys
import subprocess
import logging
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.schemas.company_schema import CompanyCreate, CompanyResponse
from app.services.company_service import create_elite_company, get_companies

router = APIRouter()
logger = logging.getLogger(__name__)


def execute_real_scraper_bot(query: str) -> None:
    """
    Hedef arama botunu bagimsiz bir alt surec olarak arkada baslatan
    ve ana sunucu bloklanmasini engelleyen yardimci fonksiyon.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
        scraper_dir = os.path.join(project_root, "scraper-bot")

        python_executable = sys.executable
        command = [python_executable, "main.py", "--sorgu", query]

        logger.info(f"OSINT tarama botu baslatiliyor: {' '.join(command)}")
        subprocess.Popen(command, cwd=scraper_dir)

    except Exception as exc:
        logger.error(f"Tarama botu alt sureci baslatilirken hata olustu: {exc}")


@router.post("/companies/scan", status_code=status.HTTP_202_ACCEPTED)
def trigger_osint_scan(background_tasks: BackgroundTasks, query: Optional[str] = Query("Denizli Tekstil")) -> Dict[
    str, str]:
    """
    Delphi arayuzunden gelen tarama istegini karsilayan ve
    sureci arkaplan gorevlerine devreden uc nokta.
    """
    background_tasks.add_task(execute_real_scraper_bot, query)
    return {"status": "success", "message": "OSINT tarama islemi arkaplanda baslatildi."}


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    """
    Nitelikli sirket ve iliskili yetkili verilerini veritabanina
    kaydeden veya mevcutsa guncelleyen uc nokta.
    """
    try:
        company_model = create_elite_company(db, company)
        return company_model
    except Exception as exc:
        logger.error(f"Sirket kaydi olusturulurken hata olustu: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Veritabanı islemi sirasinda bir ic sunucu hatası olustu."
        )


@router.get("/companies", response_model=List[CompanyResponse])
def list_companies(
        city: Optional[str] = Query(None, alias="sehir"),
        industry: Optional[str] = Query(None, alias="sektor"),
        min_confidence: int = Query(85, alias="min_puan", ge=0, le=100),
        limit: int = Query(50, ge=1, le=200),
        skip: int = Query(0, ge=0),
        db: Session = Depends(get_db),
) -> List[Company]:
    """
    Delphi istemcisinin filtreleme parametreleriyle uyumlu,
    sayfalama destekli sirket listeleme uc noktası.
    """
    try:
        companies = get_companies(
            db,
            city=city,
            industry=industry,
            min_confidence=min_confidence,
            limit=limit,
            skip=skip
        )
        return companies
    except Exception as exc:
        logger.error(f"Sirket listesi alinirken hata olustu: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Veri listeleme islemi sirasinda bir ic sunucu hatası olustu."
        )