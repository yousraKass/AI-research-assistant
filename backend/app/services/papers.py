from pathlib import Path
import hashlib
import json
import os
import logging

import httpx

from ..tools import semantic_scholar
from ..tools import arxiv as arxiv_tool

logger = logging.getLogger(__name__)


# simple on-disk cache directory (backend/cache)
CACHE_DIR = Path(__file__).resolve().parents[1].parent / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(q: str, source: str, limit: int) -> str:
    key_raw = f"{source}::limit={limit}::query={q}"
    return hashlib.sha256(key_raw.encode('utf-8')).hexdigest()


def _cache_get(key: str):
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # On any read/parse error treat as cache miss
        return None


def _cache_set(key: str, obj):
    path = CACHE_DIR / f"{key}.json"
    tmp = path.with_suffix('.json.tmp')
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        # best effort: ignore cache write failures
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def search(query: str, source: str = 'semantic_scholar', limit: int = 10) -> dict:
    """Search papers from selected sources and return normalized response.

    Returns a dict: { 'query': q, 'source': source, 'results': [ ... ] }
    """
    source = (source or 'semantic_scholar').lower()
    try:
        results = []
        # Check cache first
        key = _cache_key(query, source, limit)
        cached = _cache_get(key)
        if cached is not None:
            return cached

        if source in ('semantic_scholar', 'all'):
            ss = semantic_scholar.search_papers(query, limit=limit)
            for p in ss:
                results.append({
                    'title': p.get('title'),
                    'abstract': p.get('abstract'),
                    'authors': p.get('authors') or [],
                    'year': p.get('year'),
                    'url': p.get('url'),
                    'source': 'semantic_scholar',
                })

        if source in ('arxiv', 'all'):
            ax = arxiv_tool.search_papers(query, limit=limit)
            for p in ax:
                results.append({
                    'title': p.get('title'),
                    'abstract': p.get('abstract'),
                    'authors': p.get('authors') or [],
                    'year': p.get('year'),
                    'url': p.get('url'),
                    'source': 'arxiv',
                })

        resp = {'query': query, 'source': source, 'results': results}
        # Cache successful response for future requests (best-effort)
        try:
            _cache_set(key, resp)
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:
        # propagate upstream http errors to callers
        raise
    except Exception as e:
        logger.exception('papers.search failed: %s', e)
        raise
