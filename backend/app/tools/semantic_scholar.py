import httpx


SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# Without a key you get 100 requests / 5 minutes, shared with other unauthenticated
# traffic — fine for development, but expect occasional 429s once you're testing
# more heavily (Phase 1 will add caching + retry to handle this).
FIELDS = "title,abstract,authors,year,citationCount,paperId,url"


def search_papers(query: str, limit: int = 10) -> list[dict]:
    """
    Search Semantic Scholar for papers matching `query`.

    Returns a list of dicts with: title, abstract, authors, year,
    citation_count, paper_id, url. Papers with no abstract are skipped,
    since an empty abstract is useless for the summarization step later.
    """
    params = {
        "query": query,
        "limit": limit,
        "fields": FIELDS,
    }

    response = httpx.get(SEMANTIC_SCHOLAR_BASE_URL, params=params, timeout=10.0)
    response.raise_for_status()

    data = response.json()
    raw_papers = data.get("data", [])

    papers = []
    for paper in raw_papers:
        # abstract = paper.get("abstract")
        # if not abstract:
        #     continue  # skip papers with no abstract, nothing to summarize

        papers.append({
            "paper_id": paper.get("paperId"),
            "title": paper.get("title"),
            "abstract": paper.get("abstract"),
            "authors": [a.get("name") for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "citation_count": paper.get("citationCount"),
            "url": paper.get("url"),
        })

    return papers


if __name__ == "__main__":
    results = search_papers("GRPO reasoning LLM", limit=5)
    for r in results:
        print(f"{r['title']} ({r['year']}) — {r['citation_count']} citations")
        print(f"  {r['abstract'][:150]}...\n")