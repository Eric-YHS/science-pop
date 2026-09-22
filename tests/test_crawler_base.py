"""Crawler base-class behaviour (deduplication and persistence).

The tests drive the coroutine API directly with ``asyncio.run`` so the suite does
not need an asyncio pytest plugin.
"""

import asyncio

from app.services.crawler.base import BaseCrawler, PaperData


class FakeResult:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class FakeSession:
    """Minimal stand-in for the parts of AsyncSession the crawler uses."""

    def __init__(self, existing=None):
        self.existing = existing
        self.added = []
        self.flushed = 0

    async def execute(self, _query):
        return FakeResult(self.existing)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed += 1


class DummyCrawler(BaseCrawler):
    name = "dummy"

    async def fetch_paper_list(self):
        return [PaperData(title="A paper", source_url="https://example.org/a")]

    async def download_paper(self, paper_data, save_dir):
        return f"{save_dir}/a.pdf"


def _crawler(session):
    return DummyCrawler(db=session, discipline_id=1, max_papers=10)


def test_paper_data_defaults_are_all_optional():
    data = PaperData(title="only a title")
    assert data.authors is None
    assert data.abstract is None
    assert data.doi is None
    assert data.file_url is None


def test_save_paper_persists_a_new_paper():
    session = FakeSession(existing=None)
    crawler = _crawler(session)
    data = PaperData(title="A paper", source_url="https://example.org/a")

    paper = asyncio.run(crawler.save_paper(data, "/tmp/a.pdf", "pdf", crawl_task_id=3))

    assert paper is not None
    assert paper.title == "A paper"
    assert paper.status == "pending"
    assert paper.discipline_id == 1
    assert paper.crawl_task_id == 3
    assert session.added == [paper]
    assert session.flushed == 1


def test_save_paper_skips_duplicates_by_source_url():
    session = FakeSession(existing=object())
    crawler = _crawler(session)
    data = PaperData(title="A paper", source_url="https://example.org/a")

    assert asyncio.run(crawler.save_paper(data, None, "pdf", crawl_task_id=3)) is None
    assert session.added == []
