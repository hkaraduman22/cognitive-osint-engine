from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


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
    confidence_score: int = Field(..., ge=85, le=100)
    officials: Optional[List[CompanyOfficialCreate]] = None

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
    confidence_score: int
    created_at: datetime
    officials: List[CompanyOfficialResponse]

    model_config = ConfigDict(from_attributes=True)
