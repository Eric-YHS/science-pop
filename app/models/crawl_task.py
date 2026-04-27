from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Column(Integer, primary_key=True)
    source_name = Column(String(100), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"))
    status = Column(String(20), default="running")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    papers_found = Column(Integer, default=0)
    papers_saved = Column(Integer, default=0)
    error_log = Column(Text)

    discipline = relationship("Discipline", back_populates="crawl_tasks")
    papers = relationship("Paper", back_populates="crawl_task")
