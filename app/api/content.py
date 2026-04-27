from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Content, Paper
from app.schemas.content import ContentResponse, ContentListResponse

router = APIRouter(prefix="/contents", tags=["contents"])


@router.get("", response_model=ContentListResponse)
async def list_contents(
    paper_id: int | None = None,
    workflow_type: str | None = None,
    business_line: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Content)
    count_query = select(func.count(Content.id))

    if paper_id:
        query = query.where(Content.paper_id == paper_id)
        count_query = count_query.where(Content.paper_id == paper_id)
    if workflow_type:
        query = query.where(Content.workflow_type == workflow_type)
        count_query = count_query.where(Content.workflow_type == workflow_type)
    if business_line:
        query = query.where(Content.business_line == business_line)
        count_query = count_query.where(Content.business_line == business_line)

    total = (await db.execute(count_query)).scalar_one()
    items = (
        await db.execute(
            query.order_by(Content.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    return ContentListResponse(total=total, items=items)


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: AsyncSession = Depends(get_db)):
    content = (await db.execute(select(Content).where(Content.id == content_id))).scalar_one_or_none()
    if not content:
        raise HTTPException(404, "Content not found")
    return content
