import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal, get_db
from app.models.company import Company
from app.repositories.bot_log_repository import BotLogRepository
from app.schemas.company_schema import CompanyCreate, CompanyResponse, ScanStatusResponse
from app.services.company_service import create_elite_company, get_companies
from app.utils.dependencies import get_current_user, get_current_user_optional

router = APIRouter()
logger = logging.getLogger(__name__)


def resolve_scraper_directory() -> Path:
    """Scraper dizinini Windows çalışma alanında veya Docker container'ında bulur."""
    configured_path = os.getenv("SCRAPER_BOT_PATH")
    candidates: list[Path] = []
    if configured_path:
        candidates.append(Path(configured_path))

    current_file = Path(__file__).resolve()
    candidates.extend(parent / "scraper-bot" for parent in current_file.parents)
    candidates.append(Path("/app/scraper-bot"))

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_dir() and (resolved / "main.py").is_file():
            return resolved

    checked_paths = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"scraper-bot dizini bulunamadı. Kontrol edilen yollar: {checked_paths}")


def execute_real_scraper_bot(query: str, user_id: int | None, search_history_id: int | None = None) -> None:
    """
    Hedef arama botunu ayri bir alt surec olarak calistiran ve durumunu
    (processing/finished/error) BotLog tablosuna yazan yardimci fonksiyon.
    FastAPI BackgroundTasks icinde (istek/yanit dongusunden bagimsiz) calisir,
    bu yuzden kendi DB oturumunu acip kapatir.

    NOT: "finished" durumu yalnizca tarayici alt surecinin (URL toplama +
    kuyruga yazma) bittigini gosterir. Asenkron LLM analizi (worker container)
    ayri bir surectir ve bu adimdan sonra da devam edebilir; sonuclar bu yuzden
    "finished" sonrasinda da veritabanina eklenmeye devam edebilir.
    """
    db = SessionLocal()
    bot_log_repository = BotLogRepository(db)
    log_entry = bot_log_repository.create(
        user_id=user_id, query=query, status="processing", search_history_id=search_history_id
    )
    try:
        scraper_dir = resolve_scraper_directory()

        python_executable = sys.executable
        command = [python_executable, "main.py", "--sorgu", query]
        if search_history_id is not None:
            command.extend(["--search-history-id", str(search_history_id)])

        logger.info(f"OSINT tarama botu baslatiliyor: {' '.join(command)}")
        result = subprocess.run(command, cwd=str(scraper_dir), timeout=180)

        if result.returncode == 0:
            bot_log_repository.update_status(log_entry.id, status="finished")
        else:
            bot_log_repository.update_status(
                log_entry.id, status="error", message=f"Scraper çıkış kodu: {result.returncode}"
            )
    except subprocess.TimeoutExpired:
        bot_log_repository.update_status(log_entry.id, status="error", message="Tarama zaman aşımına uğradı (180sn)")
    except Exception as exc:
        logger.error(f"Tarama botu alt sureci baslatilirken hata olustu: {exc}")
        bot_log_repository.update_status(log_entry.id, status="error", message=str(exc))
    finally:
        db.close()


@router.post("/companies/scan", status_code=status.HTTP_202_ACCEPTED)
def trigger_osint_scan(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Query("Denizli Tekstil"),
    search_history_id: Optional[int] = Query(None, ge=1),
    current_user: Optional[dict] = Depends(get_current_user_optional),
) -> Dict[str, str]:
    """
    Delphi arayuzunden gelen tarama istegini karsilayan ve
    sureci arkaplan gorevlerine devreden uc nokta.

    NOT: Auth burada opsiyoneldir - eski/derlenmemis Delphi istemciler bu uc noktaya
    token gondermeden istek atabiliyor (bkz. proje gecmisi). Token varsa yine de
    dogrulanir ve user_id BotLog'a yazilir; yoksa istek reddedilmez, sadece user_id
    bilinmez (None) olarak kaydedilir.
    """
    user_id = current_user["id"] if current_user else None
    background_tasks.add_task(execute_real_scraper_bot, query, user_id, search_history_id)
    return {"status": "success", "message": "OSINT tarama islemi arkaplanda baslatildi."}


@router.get("/companies/scan-status", response_model=ScanStatusResponse)
def get_scan_status(
    search_history_id: int = Query(..., alias="arama_id", ge=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanStatusResponse:
    """
    Delphi'nin polling ile sorgulayacağı, bir aramaya ait en son tarama
    durumunu (processing/finished/error) döndüren uç nokta.
    """
    bot_log_repository = BotLogRepository(db)
    log_entry = bot_log_repository.get_latest_by_search_history_id(search_history_id)
    if log_entry is None:
        return ScanStatusResponse(status="pending")
    return ScanStatusResponse(status=log_entry.status, message=log_entry.message, updated_at=log_entry.updated_at)


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
