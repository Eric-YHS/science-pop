from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Paper


@dataclass
class PaperData:
    title: str
    authors: str | None = None
    abstract: str | None = None
    source_url: str | None = None
    doi: str | None = None
    file_url: str | None = None
    metadata_text: str | None = None


class BaseCrawler(ABC):
    name: str

    def __init__(self, db: AsyncSession, discipline_id: int, max_papers: int = 50):
        self.db = db
        self.discipline_id = discipline_id
        self.max_papers = max_papers

    @abstractmethod
    async def fetch_paper_list(self) -> list[PaperData]:
        """Fetch recent paper metadata from the source."""
        ...

    @abstractmethod
    async def download_paper(self, paper_data: PaperData, save_dir: str) -> str | None:
        """Download paper file, return local file path or None."""
        ...

    async def save_paper(self, paper_data: PaperData, file_path: str | None, file_type: str, crawl_task_id: int) -> Paper | None:
        exists = (
            await self.db.execute(
                select(Paper).where(Paper.source_url == paper_data.source_url)
            )
        ).scalar_one_or_none()
        if exists:
            return None

        paper = Paper(
            title=paper_data.title,
            authors=paper_data.authors,
            abstract=paper_data.abstract,
            source_url=paper_data.source_url,
            doi=paper_data.doi,
            discipline_id=self.discipline_id,
            file_path=file_path,
            file_type=file_type,
            metadata_text=paper_data.metadata_text,
            crawl_task_id=crawl_task_id,
            status="pending",
        )
        self.db.add(paper)
        await self.db.flush()
        return paper


from sqlalchemy import select  # noqa: E402
