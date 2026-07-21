from fastapi import APIRouter, status

from app.schemas.schemas import BotErrorCreate, BotLogResponse

router = APIRouter()


@router.post("/logs/bot-errors", status_code=status.HTTP_201_CREATED)
def create_bot_error(log: BotErrorCreate):
    # Bot hataları için kayıt kapısı; gerçek kayıt ileride servis katmanında yazılacak
    return {"message": "Bot hatası kaydedildi"}


@router.get("/admin/logs", response_model=list[BotLogResponse])
def admin_logs():
    # Admin log listesi gerçek veri kaynağına bağlanacak
    return []