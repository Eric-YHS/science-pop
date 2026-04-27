from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import CrawlTask, Discipline
from app.services.crawler.arxiv import ArxivCrawler
from app.services.crawler.pubmed import PubMedCrawler
from app.utils.disciplines import DISCIPLINES, SOURCE_DISCIPLINE_MAP

CRAWLERS = {
    "arXiv.org": ArxivCrawler,
    "PubMed Central": PubMedCrawler,
}


class CrawlScheduler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_all(self) -> list[CrawlTask]:
        tasks = []
        for disc_data in DISCIPLINES:
            disc = (
                await self.db.execute(select(Discipline).where(Discipline.slug == disc_data["slug"]))
            ).scalar_one_or_none()
            if not disc:
                continue
            disc_tasks = await self.run_discipline(disc)
            tasks.extend(disc_tasks)
        return tasks

    async def run_discipline(self, discipline: Discipline) -> list[CrawlTask]:
        tasks = []
        sources = discipline.sources or []
        for source_info in sources:
            source_name = source_info.get("name", "")
            crawler_cls = CRAWLERS.get(source_name)
            if not crawler_cls:
                continue

            task = await self._run_crawler(crawler_cls, discipline.id, source_name)
            if task:
                tasks.append(task)
        return tasks

    async def run_source(self, source_name: str) -> list[CrawlTask]:
        slug = SOURCE_DISCIPLINE_MAP.get(source_name)
        if not slug:
            return []

        disc = (await self.db.execute(select(Discipline).where(Discipline.slug == slug))).scalar_one_or_none()
        if not disc:
            return []

        crawler_cls = CRAWLERS.get(source_name)
        if not crawler_cls:
            return []

        task = await self._run_crawler(crawler_cls, disc.id, source_name)
        return [task] if task else []

    async def _run_crawler(self, crawler_cls, discipline_id: int, source_name: str) -> CrawlTask | None:
        crawl_task = CrawlTask(
            source_name=source_name,
            discipline_id=discipline_id,
            status="running",
        )
        self.db.add(crawl_task)
        await self.db.flush()

        crawler = crawler_cls(
            db=self.db,
            discipline_id=discipline_id,
            max_papers=settings.CRAWL_MAX_PAPERS_PER_SOURCE,
        )

        try:
            papers_data = await crawler.fetch_paper_list()
            crawl_task.papers_found = len(papers_data)

            saved = 0
            for paper_data in papers_data:
                file_path = await crawler.download_paper(paper_data, str(settings.papers_dir))
                file_type = "pdf" if file_path and file_path.endswith(".pdf") else "txt"
                paper = await crawler.save_paper(paper_data, file_path, file_type, crawl_task.id)
                if paper:
                    saved += 1

            crawl_task.papers_saved = saved
            crawl_task.status = "completed"
        except Exception as e:
            crawl_task.status = "failed"
            crawl_task.error_log = str(e)

        crawl_task.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return crawl_task
