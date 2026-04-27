import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

from app.services.crawler.base import BaseCrawler, PaperData

ARXIV_API = "http://export.arxiv.org/api/query"


class ArxivCrawler(BaseCrawler):
    name = "arXiv.org"

    async def fetch_paper_list(self) -> list[PaperData]:
        params = {
            "search_query": "cat:cs.AI OR cat:cs.CL OR cat:cs.LG",
            "start": 0,
            "max_results": self.max_papers,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(ARXIV_API, params=params)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []

        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            authors = ", ".join(a.find("atom:name", ns).text for a in entry.findall("atom:author", ns))
            abstract = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            url = entry.find("atom:id", ns).text.strip()

            doi_elem = entry.find("arxiv:doi", {"arxiv": "http://arxiv.org/schemas/atom"})
            doi = doi_elem.text.strip() if doi_elem is not None else None

            pdf_link = None
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    pdf_link = link.get("href")
                    break

            papers.append(PaperData(
                title=title,
                authors=authors,
                abstract=abstract,
                source_url=url,
                doi=doi,
                file_url=pdf_link,
                metadata_text=f"Source: arXiv\nDOI: {doi or 'N/A'}\nURL: {url}",
            ))

        return papers

    async def download_paper(self, paper_data: PaperData, save_dir: str) -> str | None:
        if not paper_data.file_url:
            return None

        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        file_name = paper_data.source_url.split("/")[-1].replace(":", "_") + ".pdf"
        file_path = save_path / file_name

        if file_path.exists():
            return str(file_path)

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.get(paper_data.file_url, follow_redirects=True)
                resp.raise_for_status()
                file_path.write_bytes(resp.content)
                return str(file_path)
            except httpx.HTTPError:
                return None
