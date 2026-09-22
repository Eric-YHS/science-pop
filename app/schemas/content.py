from datetime import datetime

from pydantic import BaseModel


class ContentResponse(BaseModel):
    id: int
    paper_id: int
    workflow_type: str
    business_line: str
    article_text: str | None = None
    image_paths: list[str] = []
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    total: int
    items: list[ContentResponse]
