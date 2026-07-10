from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
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
    search_links = relationship("SearchHistoryCompany", back_populates="company", cascade="all, delete-orphan")


class CompanyOfficial(Base):
    __tablename__ = "company_officials"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = Column(Integer, ForeignKey("companies.id"), nullable=False)
    full_name: Mapped[str] = Column(String(256), nullable=False)
    title: Mapped[str] = Column(String(256), nullable=False)
    linkedin_url: Mapped[str | None] = Column(String(512), nullable=True)

    company = relationship("Company", back_populates="officials")


class SearchHistoryCompany(Base):
    __tablename__ = "search_history_companies"
    __table_args__ = (UniqueConstraint("search_history_id", "company_id", name="uq_search_history_company"),)

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    search_history_id: Mapped[int] = Column(Integer, ForeignKey("search_history.id"), nullable=False, index=True)
    company_id: Mapped[int] = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    confidence_score: Mapped[int] = Column(Integer, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    search_history = relationship("SearchHistory", back_populates="company_links")
    company = relationship("Company", back_populates="search_links")
