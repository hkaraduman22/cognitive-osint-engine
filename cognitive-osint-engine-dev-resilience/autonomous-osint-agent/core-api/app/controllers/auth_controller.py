from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schemas import LogoutRequestDTO, MeDTO, RefreshRequestDTO, TokenDTO, UserLoginDTO, UserRegisterDTO
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenDTO)
def register(user: UserRegisterDTO, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        _, access_token, refresh_token = auth_service.register_user(user.username, user.password)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/login", response_model=TokenDTO)
def login(user: UserLoginDTO, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        _, access_token, refresh_token = auth_service.authenticate_user(user.username, user.password)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri")


@router.post("/refresh", response_model=TokenDTO)
def refresh(body: RefreshRequestDTO, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        access_token, refresh_token = auth_service.refresh_access_token(body.refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: LogoutRequestDTO, db: Session = Depends(get_db)):
    AuthService(db).logout(body.refresh_token)


@router.get("/me", response_model=MeDTO)
def me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    profile = auth_service.get_current_user_profile(user_id=current_user["id"])
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
    return profile
