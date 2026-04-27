from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    workflow_type = Column(String(20), nullable=False)  # gpt / banana
    business_line = Column(String(20), nullable=False)  # internal / external
    article_text = Column(Text)
    image_paths = Column(JSONB, default=list)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    paper = relationship("Paper", back_populates="contents")
