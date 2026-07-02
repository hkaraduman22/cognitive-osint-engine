from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schemas import TokenDTO, UserDTO, UserLoginDTO, UserRegisterDTO
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenDTO)
def register(user: UserRegisterDTO, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        _, access_token = auth_service.register_user(user.username, user.password)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/login", response_model=TokenDTO)
def login(user: UserLoginDTO, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        _, access_token = auth_service.authenticate_user(user.username, user.password)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri")
