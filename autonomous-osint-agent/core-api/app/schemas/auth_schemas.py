from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(from_attributes=True)
