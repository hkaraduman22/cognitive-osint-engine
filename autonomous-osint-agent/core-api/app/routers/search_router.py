import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.database import get_db
from app.models.company import Company, CompanyOfficial
from app.schemas.company_schema import CompanyResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search/advanced", response_model=List[CompanyResponse])
def advanced_search(
    city: Optional[str] = Query(None, description="Filtre par ville (ex: Ankara)"),
    industry: Optional[str] = Query(None, description="Filtre par secteur (ex: Otomotiv, Yazılım)"),
    min_company_size: Optional[str] = Query(None, description="Filtre par taille (ex: 500+)"),
    has_title: Optional[str] = Query(None, description="Filtre les entreprises ayant ce poste (ex: CTO)"),
    has_investment: Optional[bool] = Query(False, description="Filtre pour les entreprises ayant des investissements"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[Company]:
    """
    Endpoint de recherche avancée pour filtrer finement les entreprises et leurs employés.
    """
    try:
        query = db.query(Company).options(joinedload(Company.officials))

        if city:
            query = query.filter(Company.city.ilike(f"%{city}%"))
        
        if industry:
            query = query.filter(Company.industry.ilike(f"%{industry}%"))
            
        if min_company_size:
            # Recherche textuelle simple pour l'exemple
            query = query.filter(Company.company_size.ilike(f"%{min_company_size}%"))
            
        if has_title:
            query = query.join(Company.officials).filter(CompanyOfficial.title.ilike(f"%{has_title}%"))
            
        if has_investment:
            # Hypothèse: l'info d'investissement est dans le champ "description"
            query = query.filter(Company.description.ilike("%yatırım%"))

        companies = query.offset(skip).limit(limit).all()
        return companies

    except Exception as exc:
        logger.error(f"Erreur lors de la recherche avancée: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la recherche."
        )
