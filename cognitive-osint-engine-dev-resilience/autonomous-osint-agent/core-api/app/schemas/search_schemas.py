from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SearchRequestDTO(BaseModel):
    query: str = Field(..., min_length=1, max_length=512)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Arama sorgusu boş olamaz.")
        return normalized


class SearchResponseDTO(BaseModel):
    message: str
    search_history_id: int


class SearchHistoryDTO(BaseModel):
    id: int
    query: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecordDTO(BaseModel):
    id: int
    title: str
    content: str
    source: Optional[str]
    score: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BotLogDTO(BaseModel):
    id: int
    query: str
    status: str
    message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserSearchHistoryDTO(BaseModel):
    search_history_id: int
    query: str
    created_at: datetime
    status: str
    company_count: int


class AdminSearchHistoryCompanyDTO(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    city: Optional[str]
    confidence_score: int
    address: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    source_url: Optional[str]


class AdminSearchHistoryDetailDTO(BaseModel):
    search_history_id: int
    query: str
    created_at: datetime
    status: str
    companies: list[AdminSearchHistoryCompanyDTO]
