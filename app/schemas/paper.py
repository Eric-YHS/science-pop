from datetime import datetime

from pydantic import BaseModel


class PaperBase(BaseModel):
    title: str
    authors: str | None = None
    abstract: str | None = None
    source_url: str | None = None
    doi: str | None = None


class PaperCreate(PaperBase):
    discipline_id: int | None = None
    file_type: str | None = "pdf"


class PaperResponse(PaperBase):
    id: int
    discipline_id: int | None = None
    file_path: str | None = None
    file_type: str | None = None
    metadata_text: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaperListResponse(BaseModel):
    total: int
    items: list[PaperResponse]


class DisciplineResponse(BaseModel):
    """A discipline and the paper sources configured for it."""

    id: int
    name: str
    slug: str
    sources: list[dict] = []

    model_config = {"from_attributes": True}
