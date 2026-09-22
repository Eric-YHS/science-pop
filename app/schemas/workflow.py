
from pydantic import BaseModel


class WorkflowConvertRequest(BaseModel):
    paper_id: int
    workflow_type: str  # gpt / banana
    business_line: str  # internal / external


class WorkflowStatusResponse(BaseModel):
    content_id: int
    status: str


class CrawlTriggerRequest(BaseModel):
    source_name: str | None = None
    discipline_slug: str | None = None


class CrawlTaskResponse(BaseModel):
    id: int
    source_name: str
    discipline_id: int | None = None
    status: str
    started_at: str | None = None
    completed_at: str | None = None
    papers_found: int
    papers_saved: int

    model_config = {"from_attributes": True}
