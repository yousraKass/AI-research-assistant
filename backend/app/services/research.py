from typing import List, Optional
import json
import logging

from pydantic import BaseModel, Field

from . import papers as papers_service
from ..llm import provider
from ..llm.prompt_loader import load_prompt_template

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


class SynthesisResult(BaseModel):
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


def _parse_synthesis(raw) -> dict:
    if raw is None:
        return {
            'common_findings': '',
            'differences': '',
            'limitations': '',
        }

    if isinstance(raw, BaseModel):
        raw = raw.model_dump()

    if isinstance(raw, dict):
        return {
            'common_findings': str(raw.get('common_findings') or ''),
            'differences': str(raw.get('differences') or ''),
            'limitations': str(raw.get('limitations') or ''),
        }

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

        match = re.search(r"\{[\s\S]*\}", str(raw))
        if not match:
            return {
                'common_findings': str(raw),
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
    synthesis_template = load_prompt_template('synthesis_prompt')

    try:
        synth_result = provider.summarize_structured(summaries_text, synthesis_template, schema=SynthesisResult)
        synthesis = _parse_synthesis(synth_result)
    except Exception as e:
        logger.exception('Structured synthesis LLM call failed: %s', e)
        synthesis = {
            'common_findings': '',
            'differences': '',
            'limitations': '',
        }
    common_findings = synthesis['common_findings']
    differences = synthesis['differences']
    limitations = synthesis['limitations']

    result = ResearchReport(
        research_question=query,
        sources=[PaperSource(**s) for s in sources],
        paper_summaries=[PaperSummary(**s) for s in paper_summaries],
        common_findings=common_findings,
        differences=differences,
        limitations=limitations,
    )

    return result.model_dump()
