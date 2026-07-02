from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schemas import UserDTO
from app.schemas.search_schemas import BotLogDTO
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
