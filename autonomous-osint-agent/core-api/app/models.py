from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    city = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
