from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    sources = Column(JSONB, default=list)

    papers = relationship("Paper", back_populates="discipline")
    crawl_tasks = relationship("CrawlTask", back_populates="discipline")
