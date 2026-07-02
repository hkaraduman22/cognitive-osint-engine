from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search_schemas import SearchHistoryDTO
from app.services.search_service import SearchService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/my", response_model=list[SearchHistoryDTO])
def get_my_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = SearchService(db)
    return service.list_history(user_id=current_user["id"])
