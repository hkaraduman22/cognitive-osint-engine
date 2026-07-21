from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.models import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(256), nullable=False, index=True)
    industry: Mapped[str | None] = Column(String(256), nullable=True)
    sub_industry: Mapped[str | None] = Column(String(256), nullable=True)
    field_of_activity: Mapped[str | None] = Column(String(256), nullable=True)
    company_size: Mapped[str | None] = Column(String(128), nullable=True)
    country: Mapped[str | None] = Column(String(128), nullable=True)
    city: Mapped[str | None] = Column(String(128), nullable=True, index=True)
    website: Mapped[str | None] = Column(String(512), nullable=True)
    phone: Mapped[str | None] = Column(String(128), nullable=True)
    email: Mapped[str | None] = Column(String(256), nullable=True)
    address: Mapped[str | None] = Column(String(512), nullable=True)
    map_location: Mapped[str | None] = Column(String(256), nullable=True)
    foundation_year: Mapped[int | None] = Column(Integer, nullable=True)
    description: Mapped[str | None] = Column(String(2000), nullable=True)
    source: Mapped[str | None] = Column(String(256), nullable=True)
    confidence_score: Mapped[int] = Column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    officials = relationship("CompanyOfficial", back_populates="company", cascade="all, delete-orphan")


class CompanyOfficial(Base):
    __tablename__ = "company_officials"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = Column(Integer, ForeignKey("companies.id"), nullable=False)
    full_name: Mapped[str] = Column(String(256), nullable=False)
    title: Mapped[str] = Column(String(256), nullable=False)
    field_of_work: Mapped[str | None] = Column(String(256), nullable=True)
    city: Mapped[str | None] = Column(String(128), nullable=True)
    country: Mapped[str | None] = Column(String(128), nullable=True)
    email: Mapped[str | None] = Column(String(256), nullable=True)
    phone: Mapped[str | None] = Column(String(128), nullable=True)
    linkedin_url: Mapped[str | None] = Column(String(512), nullable=True)
    confidence_score: Mapped[int] = Column(Integer, nullable=False, default=0)

    company = relationship("Company", back_populates="officials")