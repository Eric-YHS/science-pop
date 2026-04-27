from app.database import Base
from app.models.discipline import Discipline
from app.models.paper import Paper
from app.models.crawl_task import CrawlTask
from app.models.content import Content

__all__ = ["Base", "Discipline", "Paper", "CrawlTask", "Content"]
