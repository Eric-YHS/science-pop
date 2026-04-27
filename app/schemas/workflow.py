from typing import Optional

from pydantic import BaseModel


class WorkflowConvertRequest(BaseModel):
    paper_id: int
    workflow_type: str  # gpt / banana
    business_line: str  # internal / external


class WorkflowStatusResponse(BaseModel):
    content_id: int
    status: str


class CrawlTriggerRequest(BaseModel):
    source_name: Optional[str] = None
    discipline_slug: Optional[str] = None


class CrawlTaskResponse(BaseModel):
    id: int
    source_name: str
    discipline_id: Optional[int] = None
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    papers_found: int
    papers_saved: int

    model_config = {"from_attributes": True}
