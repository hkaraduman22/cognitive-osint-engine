import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.company import Company, CompanyOfficial

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/reports/statistics", response_model=Dict[str, Any])
def get_reports_statistics(db: Session = Depends(get_db)):
    """
    Endpoint de génération de rapports statistiques.
    Retourne la distribution des entreprises par secteur, région, 
    et des statistiques sur les dirigeants.
    """
    try:
        # Sektörel analiz
        industry_distribution = dict(
            db.query(Company.industry, func.count(Company.id))
            .filter(Company.industry.isnot(None))
            .group_by(Company.industry)
            .all()
        )

        # Bölgesel analiz (Şehir bazlı)
        regional_distribution = dict(
            db.query(Company.city, func.count(Company.id))
            .filter(Company.city.isnot(None))
            .group_by(Company.city)
            .all()
        )

        # Firma büyüklüğü dağılımı
        size_distribution = dict(
            db.query(Company.company_size, func.count(Company.id))
            .filter(Company.company_size.isnot(None))
            .group_by(Company.company_size)
            .all()
        )

        # Yönetici unvan dağılımı
        title_distribution = dict(
            db.query(CompanyOfficial.title, func.count(CompanyOfficial.id))
            .group_by(CompanyOfficial.title)
            .all()
        )

        return {
            "industry_distribution": industry_distribution,
            "regional_distribution": regional_distribution,
            "company_size_distribution": size_distribution,
            "title_distribution": title_distribution,
            "total_companies": sum(industry_distribution.values()),
            "total_officials": sum(title_distribution.values())
        }

    except Exception as exc:
        logger.error(f"Erreur lors de la génération du rapport: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la génération du rapport."
        )
