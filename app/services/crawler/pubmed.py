import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

from app.services.crawler.base import BaseCrawler, PaperData

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class PubMedCrawler(BaseCrawler):
    name = "PubMed Central"

    async def fetch_paper_list(self) -> list[PaperData]:
        async with httpx.AsyncClient(timeout=30) as client:
            search_resp = await client.get(ESEARCH_URL, params={
                "db": "pmc",
                "term": "open access[filter]",
                "retmax": self.max_papers,
                "sort": "date",
                "retmode": "json",
            })
            search_resp.raise_for_status()
            id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])

            if not id_list:
                return []

            fetch_resp = await client.get(EFETCH_URL, params={
                "db": "pmc",
                "id": ",".join(id_list),
                "retmode": "xml",
            })
            fetch_resp.raise_for_status()

        root = ET.fromstring(fetch_resp.text)
        papers = []

        for article in root.findall(".//article"):
            title_elem = article.find(".//article-title")
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"

            authors_list = []
            for contrib in article.findall(".//contrib[@contrib-type='author']"):
                name = contrib.find("name")
                if name is not None:
                    surname = name.findtext("surname", "")
                    given = name.findtext("given-names", "")
                    authors_list.append(f"{given} {surname}".strip())
            authors = ", ".join(authors_list) if authors_list else None

            abstract_parts = []
            for sec in article.findall(".//abstract//p"):
                if sec.text:
                    abstract_parts.append(sec.text.strip())
            abstract = " ".join(abstract_parts) if abstract_parts else None

            article_id = article.find(".//article-id[@pub-id-type='pmc']")
            pmc_id = article_id.text if article_id is not None else None
            source_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/" if pmc_id else None

            doi_elem = article.find(".//article-id[@pub-id-type='doi']")
            doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else None

            papers.append(PaperData(
                title=title,
                authors=authors,
                abstract=abstract,
                source_url=source_url,
                doi=doi,
                metadata_text=f"Source: PubMed Central\nPMCID: PMC{pmc_id or 'N/A'}\nDOI: {doi or 'N/A'}",
            ))

        return papers

    async def download_paper(self, paper_data: PaperData, save_dir: str) -> str | None:
        if not paper_data.source_url:
            return None

        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        pmc_id = paper_data.source_url.split("PMC")[-1].rstrip("/")
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
        file_name = f"PMC{pmc_id}.pdf"
        file_path = save_path / file_name

        if file_path.exists():
            return str(file_path)

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.get(pdf_url, follow_redirects=True)
                resp.raise_for_status()
                file_path.write_bytes(resp.content)
                return str(file_path)
            except httpx.HTTPError:
                return None
