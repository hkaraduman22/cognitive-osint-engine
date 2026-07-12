from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _resolve_user(token: str, db: Session) -> dict:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz veya süresi dolmuş token")

    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")

    return {"id": user.id, "username": user.username, "is_admin": user.is_admin}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    return _resolve_user(token, db)


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Token yoksa None döner (istek reddedilmez); token varsa hâlâ gecerli olmak zorundadır.
    Eski/derlenmemiş istemcilerle geriye dönük uyumluluk gereken uc noktalarda kullanılır.
    """
    if not token:
        return None
    return _resolve_user(token, db)
