from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text)
    abstract = Column(Text)
    source_url = Column(String(1000))
    doi = Column(String(100))
    discipline_id = Column(Integer, ForeignKey("disciplines.id"))
    file_path = Column(String(500))
    file_type = Column(String(10))
    metadata_text = Column(Text)
    crawl_task_id = Column(Integer, ForeignKey("crawl_tasks.id"))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    discipline = relationship("Discipline", back_populates="papers")
    crawl_task = relationship("CrawlTask", back_populates="papers")
    contents = relationship("Content", back_populates="paper")
