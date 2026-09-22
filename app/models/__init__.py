from app.database import Base
from app.models.content import Content
from app.models.crawl_task import CrawlTask
from app.models.discipline import Discipline
from app.models.paper import Paper

__all__ = ["Base", "Discipline", "Paper", "CrawlTask", "Content"]
