import html
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import httpx
from langchain_core.tools import tool

SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_DETAIL_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper"
ARXIV_API = "https://export.arxiv.org/api/query"
DUCKDUCKGO_HTML = "https://duckduckgo.com/html/"


def _normalize_authors(author_items) -> list[str]:
    authors = []
    for author in author_items or []:
        if isinstance(author, dict):
            name = author.get("name") or author.get("full_name") or author.get("author")
            if name:
                authors.append(name)
        elif isinstance(author, str):
            authors.append(author)
    return authors


def _paper_record(
    *,
    title=None,
    abstract=None,
    authors=None,
    year=None,
    url=None,
    paper_id=None,
    citation_count=None,
) -> dict:
    record = {
        "paper_id": paper_id,
        "title": title,
        "abstract": abstract or "",
        "authors": _normalize_authors(authors),
        "year": year,
        "url": url,
    }
    if citation_count is not None:
        record["citation_count"] = citation_count
    return record


def _normalize_semantic_paper(paper: dict) -> dict:
    return _paper_record(
        paper_id=paper.get("paperId") or paper.get("paper_id"),
        title=paper.get("title"),
        abstract=paper.get("abstract"),
        authors=paper.get("authors", []) or [],
        year=paper.get("year"),
        url=paper.get("url"),
        citation_count=paper.get("citationCount"),
    )


@tool
def search_semantic_scholar(query: str, limit: int = 5) -> list[dict]:
    """Search Semantic Scholar for academic papers matching the query."""
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,citationCount,paperId,url",
    }
    response = httpx.get(SEMANTIC_SCHOLAR_BASE_URL, params=params, timeout=10.0)
    response.raise_for_status()
    data = response.json().get("data", [])
    return [_normalize_semantic_paper(paper) for paper in data]


@tool
def search_arxiv(query: str, limit: int = 5) -> list[dict]:
    """Search arXiv for scholarly papers matching the query."""
    url = f"{ARXIV_API}?search_query={quote_plus('all:' + query)}&start=0&max_results={limit}"
    response = httpx.get(url, timeout=10.0, follow_redirects=True)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        authors = [
            author.find("atom:name", ns).text
            for author in entry.findall("atom:author", ns)
            if author.find("atom:name", ns) is not None and author.find("atom:name", ns).text
        ]
        link = None
        for link_elem in entry.findall("atom:link", ns):
            if link_elem.attrib.get("type") == "text/html":
                link = link_elem.attrib.get("href")
                break
        if not link:
            id_elem = entry.find("atom:id", ns)
            link = id_elem.text if id_elem is not None else None

        year = None
        if published is not None and published.text:
            try:
                year = int(published.text[:4])
            except ValueError:
                year = None

        results.append(_paper_record(
            title=title.text.strip() if title is not None and title.text else None,
            abstract=summary.text.strip() if summary is not None and summary.text else None,
            authors=authors,
            year=year,
            url=link,
        ))

    return results


@tool
def search_web(query: str, limit: int = 5) -> list[dict]:
    """Search the public web for general results related to the query."""
    response = httpx.get(
        DUCKDUCKGO_HTML,
        params={"q": query},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10.0,
    )
    response.raise_for_status()

    html_text = response.text
    matches = re.findall(
        r'<a[^>]*class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    results = []
    for href, title_html in matches[:limit]:
        title = re.sub(r'<.*?>', '', title_html)
        results.append({
            "title": html.unescape(title).strip(),
            "url": href,
            "snippet": "",
        })

    return results


@tool
def get_paper(paper_id: str) -> dict:
    """Fetch the metadata for a specific paper using its Semantic Scholar paper ID."""
    response = httpx.get(
        f"{SEMANTIC_SCHOLAR_DETAIL_BASE_URL}/{paper_id}",
        params={"fields": "title,abstract,authors,year,url"},
        timeout=10.0,
    )
    response.raise_for_status()
    payload = response.json()
    return _normalize_semantic_paper(payload)
