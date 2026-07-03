from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequestDTO(BaseModel):
    query: str = Field(..., max_length=512)


class SearchResponseDTO(BaseModel):
    message: str


class SearchHistoryDTO(BaseModel):
    id: int
    query: str
    created_at: datetime

    class Config:
        orm_mode = True


class RecordDTO(BaseModel):
    id: int
    title: str
    content: str
    source: Optional[str]
    score: int
    created_at: datetime

    class Config:
        orm_mode = True


class BotLogDTO(BaseModel):
    id: int
    query: str
    status: str
    message: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
