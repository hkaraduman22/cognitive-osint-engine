from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.models import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(256), nullable=False, index=True)
    industry: Mapped[str] = Column(String(256), nullable=True)
    city: Mapped[str] = Column(String(128), nullable=True, index=True)
    confidence_score: Mapped[int] = Column(Integer, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    officials = relationship("CompanyOfficial", back_populates="company", cascade="all, delete-orphan")


class CompanyOfficial(Base):
    __tablename__ = "company_officials"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = Column(Integer, ForeignKey("companies.id"), nullable=False)
    full_name: Mapped[str] = Column(String(256), nullable=False)
    title: Mapped[str] = Column(String(256), nullable=False)
    linkedin_url: Mapped[str | None] = Column(String(512), nullable=True)

    company = relationship("Company", back_populates="officials")
