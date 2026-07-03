from fastapi import APIRouter, status

from app.schemas.schemas import TokenResponse, UserCreate, UserLogin

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    # İş mantığı ileride service katmanına taşınacak
    return {"access_token": "dummy-token", "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    # İş mantığı ileride service katmanına taşınacak
    return {"access_token": "dummy-token", "token_type": "bearer"}
