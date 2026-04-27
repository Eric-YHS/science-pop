import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from sqlalchemy import select

from app.api.router import api_router
from app.config import settings
from app.database import async_session, engine
from app.models import Base, Discipline
from app.utils.disciplines import DISCIPLINES

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def seed_disciplines():
    async with async_session() as db:
        for disc_data in DISCIPLINES:
            existing = (
                await db.execute(select(Discipline).where(Discipline.slug == disc_data["slug"]))
            ).scalar_one_or_none()
            if not existing:
                disc = Discipline(
                    name=disc_data["name"],
                    slug=disc_data["slug"],
                    sources=disc_data["sources"],
                )
                db.add(disc)
        await db.commit()


async def weekly_crawl():
    from app.services.crawler.scheduler import CrawlScheduler

    async with async_session() as db:
        scheduler_inst = CrawlScheduler(db)
        await scheduler_inst.run_all()
    logger.info("Weekly crawl completed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_disciplines()

    scheduler.add_job(weekly_crawl, "cron", day_of_week="sun", hour=2, minute=0, id="weekly_crawl")
    scheduler.start()
    logger.info("Scheduler started, weekly crawl on Sundays at 02:00")

    yield

    scheduler.shutdown()


app = FastAPI(
    title="科普转化平台",
    description="学术论文爬取与科普内容转化 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
