from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .company_schema import CompanyCreate, CompanyResponse


# API girişleri için: kullanıcı kayıt / login verisi
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=128)
    password: str = Field(..., min_length=8)
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
    model_config = ConfigDict(from_attributes=True)


# Delphi'ye / API istemcisine dönerken kullanılacak kullanıcı yanıtı
class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


# Arama geçmişi kaydını oluştururken kullanılacak veri transfer nesnesi
class SearchHistoryCreate(BaseModel):
    query: str = Field(..., max_length=512)
    model_config = ConfigDict(from_attributes=True)


# Delphi'ye arama geçmişi listesi dönerken kullanılacak şema
class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScraperTriggerRequest(BaseModel):
    target_domain: str
    keyword: str
    model_config = ConfigDict(from_attributes=True)


# Company DTO'ları tek kaynak olarak company_schema.py içinde tanımlanmıştır.
# Buradaki import, app.schemas.schemas üzerinden erişimi korur.


# Bot'tan LLM'den gelen personel verisi için zorunlu confidence_score alanı
class PersonnelCreate(BaseModel):
    first_name: str = Field(..., max_length=128)
    last_name: str = Field(..., max_length=128)
    title: Optional[str]
    email: Optional[str]
    company_id: Optional[int]
    confidence_score: int = Field(..., ge=0, le=100)
    model_config = ConfigDict(from_attributes=True)


# Delphi'ye veya API üzerinden personel kayıtlarını listelerken dönecek yanıt
class PersonnelResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    title: Optional[str]
    email: Optional[str]
    company_id: Optional[int]
    confidence_score: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Bot loglarının admin paneline dönerken kullanacağı şema
class BotLogResponse(BaseModel):
    id: int
    user_id: int
    query: str
    status: str
    message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BotErrorCreate(BaseModel):
    user_id: int
    query: str
    status: str
    message: Optional[str]

    model_config = ConfigDict(from_attributes=True)
