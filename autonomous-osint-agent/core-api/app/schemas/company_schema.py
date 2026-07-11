from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from urllib.parse import urlparse


class CompanyOfficialCreate(BaseModel):
    full_name: str = Field(..., max_length=256)
    title: str = Field(..., max_length=256)
    linkedin_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyCreatedOfficialResponse(BaseModel):
    id: int
    full_name: str
    title: str
    linkedin_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=256)
    industry: Optional[str] = Field(None, max_length=256)
    city: Optional[str] = Field(None, max_length=128)
    source_url: Optional[str] = Field(None, max_length=1024)
    confidence_score: int = Field(..., ge=85, le=100)
    search_history_id: Optional[int] = Field(default=None, ge=1)
    officials: Optional[List[CompanyOfficialCreate]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Firma adı boş olamaz.")
        return normalized

    @field_validator("industry", "city")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Kaynak URL http veya https adresi olmalıdır.")
        return normalized

    model_config = ConfigDict(from_attributes=True)


class CompanyOfficialResponse(BaseModel):
    id: int
    full_name: str
    title: str
    linkedin_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    city: Optional[str]
    source_url: Optional[str]
    confidence_score: int
    created_at: datetime
    updated_at: datetime
    officials: List[CompanyOfficialResponse]

    model_config = ConfigDict(from_attributes=True)
