from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schemas import UserDTO
from app.schemas.search_schemas import AdminSearchHistoryDetailDTO, AdminUserSearchHistoryDTO, BotLogDTO
from app.services.admin_service import AdminService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/users", response_model=list[UserDTO])
def list_users(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yönetici yetkisi gerekli")

    service = AdminService(db)
    return service.list_users()


@router.get("/logs", response_model=list[BotLogDTO])
def list_logs(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yönetici yetkisi gerekli")

    service = AdminService(db)
    return service.list_bot_logs()


@router.get("/users/{user_id}/search-history", response_model=list[AdminUserSearchHistoryDTO])
def list_user_search_history(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yönetici yetkisi gerekli")

    service = AdminService(db)
    return service.list_user_search_history(user_id=user_id)


@router.get("/search-history/{search_history_id}", response_model=AdminSearchHistoryDetailDTO)
def get_search_history_detail(
    search_history_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yönetici yetkisi gerekli")

    service = AdminService(db)
    detail = service.get_search_history_detail(search_history_id=search_history_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arama geçmişi bulunamadı")
    return detail
