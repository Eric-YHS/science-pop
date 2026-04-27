from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaperBase(BaseModel):
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    source_url: Optional[str] = None
    doi: Optional[str] = None


class PaperCreate(PaperBase):
    discipline_id: Optional[int] = None
    file_type: Optional[str] = "pdf"


class PaperResponse(PaperBase):
    id: int
    discipline_id: Optional[int] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    metadata_text: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaperListResponse(BaseModel):
    total: int
    items: list[PaperResponse]
