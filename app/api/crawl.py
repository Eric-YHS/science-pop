from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CrawlTask, Discipline
from app.schemas.workflow import CrawlTriggerRequest, CrawlTaskResponse
from app.services.crawler.scheduler import CrawlScheduler

router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.post("/trigger", response_model=list[CrawlTaskResponse])
async def trigger_crawl(
    request: CrawlTriggerRequest = CrawlTriggerRequest(),
    db: AsyncSession = Depends(get_db),
):
    scheduler = CrawlScheduler(db)

    if request.discipline_slug:
        disc = (
            await db.execute(select(Discipline).where(Discipline.slug == request.discipline_slug))
        ).scalar_one_or_none()
        if not disc:
            raise HTTPException(404, f"Discipline '{request.discipline_slug}' not found")
        tasks = await scheduler.run_discipline(disc)
    elif request.source_name:
        tasks = await scheduler.run_source(request.source_name)
    else:
        tasks = await scheduler.run_all()

    return tasks


@router.get("/tasks", response_model=list[CrawlTaskResponse])
async def list_crawl_tasks(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    tasks = (
        await db.execute(select(CrawlTask).order_by(CrawlTask.started_at.desc()).limit(limit))
    ).scalars().all()
    return tasks
