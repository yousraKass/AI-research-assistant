from typing import List
import json
import logging

from . import papers as papers_service
from ..llm import provider

logger = logging.getLogger(__name__)


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

        # Summarize individual paper using the project's LLM provider.
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

    # Prepare synthesis prompt: ask the LLM to synthesize only from summaries.
    summaries_text = '\n\n'.join([f"Title: {s['title']}\nSummary: {s['summary']}" for s in paper_summaries])

    # Use the synthesis prompt template via prompt loader (provider supports loading by name)
    synthesis_input = summaries_text
    try:
        synth_raw = provider.summarize(synthesis_input, 'synthesis_prompt')
    except Exception as e:
        logger.exception('Synthesis LLM call failed: %s', e)
        synth_raw = ''

    common_findings = ''
    differences = ''
    limitations = ''

    # try to parse JSON from the LLM output
    try:
        # The model should return JSON — try to find a JSON blob
        parsed = None
        try:
            parsed = json.loads(synth_raw)
        except Exception:
            # try to locate a JSON substring
            import re

            m = re.search(r"\{[\s\S]*\}", synth_raw)
            if m:
                parsed = json.loads(m.group(0))

        if isinstance(parsed, dict):
            common_findings = parsed.get('common_findings') or parsed.get('common_findings', '')
            differences = parsed.get('differences') or parsed.get('differences', '')
            limitations = parsed.get('limitations') or parsed.get('limitations', '')
        else:
            # fallback: put entire synthesis text into common_findings
            common_findings = synth_raw or ''
    except Exception:
        logger.exception('Failed to parse synthesis output; returning raw text')
        common_findings = synth_raw or ''

    result = {
        'research_question': query,
        'sources': sources,
        'paper_summaries': paper_summaries,
        'common_findings': common_findings,
        'differences': differences,
        'limitations': limitations,
    }

    return result
