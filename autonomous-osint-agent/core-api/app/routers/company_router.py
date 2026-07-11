import os
import sys
import subprocess
import logging
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.company import Company
from app.schemas.company_schema import CompanyCreate, CompanyResponse
from app.services.company_service import create_elite_company, get_companies
from app.utils.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def execute_real_scraper_bot(query: str, search_history_id: int | None = None) -> None:
    """
    Hedef arama botunu bagimsiz bir alt surec olarak arkada baslatan
    ve ana sunucu bloklanmasini engelleyen yardimci fonksiyon.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
        scraper_dir = os.path.join(project_root, "scraper-bot")

        python_executable = sys.executable
        command = [python_executable, "main.py", "--sorgu", query]
        if search_history_id is not None:
            command.extend(["--search-history-id", str(search_history_id)])

        logger.info(f"OSINT tarama botu baslatiliyor: {' '.join(command)}")
        subprocess.Popen(command, cwd=scraper_dir)

    except Exception as exc:
        logger.error(f"Tarama botu alt sureci baslatilirken hata olustu: {exc}")


@router.post("/companies/scan", status_code=status.HTTP_202_ACCEPTED)
def trigger_osint_scan(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Query("Denizli Tekstil"),
    search_history_id: Optional[int] = Query(None, ge=1),
) -> Dict[
    str, str]:
    """
    Delphi arayuzunden gelen tarama istegini karsilayan ve
    sureci arkaplan gorevlerine devreden uc nokta.
    """
    background_tasks.add_task(execute_real_scraper_bot, query, search_history_id)
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
        search_history_id: Optional[int] = Query(None, alias="arama_id", ge=1),
    current_user: dict = Depends(get_current_user),
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
            skip=skip,
            search_history_id=search_history_id,
            current_user=current_user,
        )
        return companies
    except Exception as exc:
        logger.error(f"Sirket listesi alinirken hata olustu: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Veri listeleme islemi sirasinda bir ic sunucu hatası olustu."
        )


@router.get("/stats/industry-distribution", status_code=status.HTTP_200_OK)
def get_industry_distribution(db: Session = Depends(get_db)) -> Dict[str, int]:
    """
    TEMİZ KOD: Delphi grafik arayüzünün (btnAnalizGetirClick) talep ettigi,
    sirketlerin sektorlerine gore dagılım sayılarını donen uc nokta.
    """
    try:
        # Sektör gruplarına göre şirket sayılarını sayan SQL sorgusu
        query_results = (
            db.query(Company.industry, func.count(Company.id))
            .group_by(Company.industry)
            .all()
        )

        # Sonuçların Delphi TJSONObject yapısına uygun düz bir sözlüğe dönüştürülmesi
        distribution_map: Dict[str, int] = {}
        for industry, count in query_results:
            if industry:
                distribution_map[str(industry)] = int(count)

        return distribution_map

    except Exception as exc:
        logger.error(f"Sektorel dagılım istatistikleri hesaplanırken hata olustu: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Istatistik verileri uretilirken bir ic sunucu hatası olustu."
        )
