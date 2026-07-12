from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.utils.security import decode_access_token

# NOT: Daha once OAuth2PasswordBearer kullaniliyordu; bu, Swagger'in "Authorize"
# penceresinde kullanici adi/sifre ile giris yapmayi VE bunu form-encoded olarak
# /auth/login'e POST etmeyi deniyordu. /auth/login ise JSON govde bekledigi icin
# bu her zaman 422 Unprocessable Entity ile basarisiz oluyordu. HTTPBearer ile
# Swagger sadece tek bir "token yapistir" kutusu gosterir - gercek akisimizla
# (once /auth/login'i JSON ile cagirip token'i elle almak) uyumludur.
bearer_scheme = HTTPBearer()
bearer_scheme_optional = HTTPBearer(auto_error=False)


def _resolve_user(token: str, db: Session) -> dict:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz veya süresi dolmuş token")

    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")

    return {"id": user.id, "username": user.username, "is_admin": user.is_admin}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)
) -> dict:
    return _resolve_user(credentials.credentials, db)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """
    Token yoksa None döner (istek reddedilmez); token varsa hâlâ gecerli olmak zorundadır.
    Eski/derlenmemiş istemcilerle geriye dönük uyumluluk gereken uc noktalarda kullanılır.
    """
    if not credentials:
        return None
    return _resolve_user(credentials.credentials, db)
