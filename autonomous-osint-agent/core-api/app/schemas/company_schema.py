from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class CompanyOfficialCreate(BaseModel):
    full_name: str = Field(..., max_length=256)
    title: str = Field(..., max_length=256)
    field_of_work: Optional[str] = Field(None, max_length=256)
    city: Optional[str] = Field(None, max_length=128)
    country: Optional[str] = Field(None, max_length=128)
    email: Optional[str] = Field(None, max_length=256)
    phone: Optional[str] = Field(None, max_length=128)
    linkedin_url: Optional[str] = None
    confidence_score: int = Field(0, ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)


class CompanyOfficialResponse(BaseModel):
    id: int
    company_id: int
    full_name: str
    title: str
    field_of_work: Optional[str]
    city: Optional[str]
    country: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    confidence_score: int

    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=256)
    industry: Optional[str] = Field(None, max_length=256)
    sub_industry: Optional[str] = Field(None, max_length=256)
    field_of_activity: Optional[str] = Field(None, max_length=256)
    company_size: Optional[str] = Field(None, max_length=128)
    country: Optional[str] = Field(None, max_length=128)
    city: Optional[str] = Field(None, max_length=128)
    website: Optional[str] = Field(None, max_length=512)
    phone: Optional[str] = Field(None, max_length=128)
    email: Optional[str] = Field(None, max_length=256)
    address: Optional[str] = Field(None, max_length=512)
    map_location: Optional[str] = Field(None, max_length=256)
    foundation_year: Optional[int] = None
    description: Optional[str] = Field(None, max_length=2000)
    source: Optional[str] = Field(None, max_length=256)
    confidence_score: int = Field(..., ge=85, le=100)
    officials: Optional[List[CompanyOfficialCreate]] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    sub_industry: Optional[str]
    field_of_activity: Optional[str]
    company_size: Optional[str]
    country: Optional[str]
    city: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    map_location: Optional[str]
    foundation_year: Optional[int]
    description: Optional[str]
    source: Optional[str]
    confidence_score: int
    created_at: datetime
    updated_at: Optional[datetime]
    officials: List[CompanyOfficialResponse]

    model_config = ConfigDict(from_attributes=True)
