from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search_schemas import RecordDTO, SearchHistoryDTO, SearchRequestDTO, SearchResponseDTO
from app.services.search_service import SearchService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=SearchResponseDTO, status_code=status.HTTP_202_ACCEPTED)
def search(request: SearchRequestDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = SearchService(db)
    return service.enqueue_search(user_id=current_user["id"], query=request.query)


@router.get("/records", response_model=list[RecordDTO])
def records(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = SearchService(db)
    return service.list_records(user_id=current_user["id"])


@router.get("/history", response_model=list[SearchHistoryDTO])
def history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = SearchService(db)
    return service.list_history(user_id=current_user["id"])
