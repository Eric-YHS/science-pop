from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Paper, Content
from app.schemas.workflow import WorkflowConvertRequest, WorkflowStatusResponse
from app.services.workflow import CozeWorkflowClient

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.post("/convert", response_model=WorkflowStatusResponse)
async def trigger_conversion(
    request: WorkflowConvertRequest,
    db: AsyncSession = Depends(get_db),
):
    if request.workflow_type not in ("gpt", "banana"):
        raise HTTPException(400, "workflow_type must be 'gpt' or 'banana'")
    if request.business_line not in ("internal", "external"):
        raise HTTPException(400, "business_line must be 'internal' or 'external'")

    paper = (await db.execute(select(Paper).where(Paper.id == request.paper_id))).scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")

    content = Content(
        paper_id=paper.id,
        workflow_type=request.workflow_type,
        business_line=request.business_line,
        status="pending",
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)

    client = CozeWorkflowClient()
    await client.trigger_workflow(content.id, paper, request.workflow_type)

    return WorkflowStatusResponse(content_id=content.id, status=content.status)


@router.get("/status/{content_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(content_id: int, db: AsyncSession = Depends(get_db)):
    content = (await db.execute(select(Content).where(Content.id == content_id))).scalar_one_or_none()
    if not content:
        raise HTTPException(404, "Content not found")
    return WorkflowStatusResponse(content_id=content.id, status=content.status)
