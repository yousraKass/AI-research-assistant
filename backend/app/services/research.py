from typing import List, Optional
import json
import logging

from pydantic import BaseModel, Field

from . import papers as papers_service
from ..llm import provider

logger = logging.getLogger(__name__)


class PaperSource(BaseModel):
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    url: Optional[str] = None


class PaperSummary(BaseModel):
    title: Optional[str] = None
    summary: str = ''
    url: Optional[str] = None


class ResearchReport(BaseModel):
    research_question: str
    sources: List[PaperSource] = Field(default_factory=list)
    paper_summaries: List[PaperSummary] = Field(default_factory=list)
    common_findings: str = ''
    differences: str = ''
    limitations: str = ''


def _unique_papers(papers: List[dict]) -> List[dict]:
    seen = set()
    out = []
    for p in papers:
        pid = p.get('paper_id') or p.get('url') or p.get('title')
        key = (pid or '').strip().lower()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def _parse_synthesis(raw: str) -> dict:
    if not raw:
        return {
            'common_findings': '',
            'differences': '',
            'limitations': '',
        }

    try:
        parsed = json.loads(raw)
    except Exception:
        import re

        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            return {
                'common_findings': raw,
                'differences': '',
                'limitations': '',
            }
        parsed = json.loads(match.group(0))

    if isinstance(parsed, dict):
        return {
            'common_findings': str(parsed.get('common_findings') or ''),
            'differences': str(parsed.get('differences') or ''),
            'limitations': str(parsed.get('limitations') or ''),
        }

    return {
        'common_findings': str(raw),
        'differences': '',
        'limitations': '',
    }


def research(query: str, limit: int = 6) -> dict:
    """Run a small research workflow for `query`.

    Steps:
    - search Semantic Scholar
    - filter papers (must have abstract, dedupe)
    - summarize each paper via LLM
    - synthesize summaries into findings/differences/limitations

    Returns structured dict described in the project spec.
    """
    # fetch a few extra to allow filtering + dedupe
    fetch_limit = max(limit * 2, limit + 2)
    resp = papers_service.search(query, source='semantic_scholar', limit=fetch_limit)
    raw = resp.get('results', [])

    # filter: require abstract
    candidates = [p for p in raw if p.get('abstract')]

    # dedupe
    unique = _unique_papers(candidates)

    # limit to requested number
    selected = unique[:limit]

    if not selected:
        return ResearchReport(
            research_question=query,
            sources=[],
            paper_summaries=[],
            common_findings='No relevant papers with usable abstracts were found for this query.',
            differences='',
            limitations='No paper-level evidence was available for synthesis.',
        ).model_dump()

    sources = []
    paper_summaries = []

    for p in selected:
        title = p.get('title')
        abstract = p.get('abstract') or ''
        authors = p.get('authors') or []
        year = p.get('year')
        url = p.get('url')

        sources.append({
            'title': title,
            'authors': authors,
            'year': year,
            'url': url,
        })

        try:
            summary = provider.summarize(abstract, 'paper_summarization')
        except Exception as e:
            logger.exception('Failed to summarize paper %s: %s', title, e)
            summary = '[SUMMARY ERROR] Could not summarize this paper.'

        paper_summaries.append({
            'title': title,
            'summary': summary,
            'url': url,
        })

    summaries_text = '\n\n'.join([f"Title: {s['title']}\nSummary: {s['summary']}" for s in paper_summaries])

    try:
        synth_raw = provider.summarize(summaries_text, 'synthesis_prompt')
    except Exception as e:
        logger.exception('Synthesis LLM call failed: %s', e)
        synth_raw = ''

    synthesis = _parse_synthesis(synth_raw)
    common_findings = synthesis['common_findings'] or 'No shared findings could be confidently extracted from the summarized papers.'
    differences = synthesis['differences'] or 'No substantive disagreements or method differences were explicitly identified in the supplied summaries.'
    limitations = synthesis['limitations'] or 'No explicit limitations were identified in the supplied paper summaries.'

    result = ResearchReport(
        research_question=query,
        sources=[PaperSource(**s) for s in sources],
        paper_summaries=[PaperSummary(**s) for s in paper_summaries],
        common_findings=common_findings,
        differences=differences,
        limitations=limitations,
    )

    return result.model_dump()
