from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRegisterDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=128)
    password: str = Field(..., min_length=8)


class UserLoginDTO(BaseModel):
    username: str
    password: str


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserDTO(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True
