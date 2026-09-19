from fastapi import APIRouter, Query, HTTPException
from typing import List
import hashlib
import json
import os
from pathlib import Path

import httpx

from ..tools import semantic_scholar
from ..tools import arxiv as arxiv_tool


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

router = APIRouter()


@router.get('/papers/search')
async def papers_search(q: str = Query(..., min_length=1), source: str = Query('semantic_scholar'), limit: int = Query(10, ge=1, le=100)):
    """Search papers from a selected source.

    Query params:
    - q: query string
    - source: 'semantic_scholar' | 'arxiv' | 'all'
    """
    source = source.lower()
    try:
        results = []
        # Check cache first
        key = _cache_key(q, source, limit)
        cached = _cache_get(key)
        if cached is not None:
            return cached
        if source in ('semantic_scholar', 'all'):
            ss = semantic_scholar.search_papers(q, limit=limit)
            # Normalize fields
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
            ax = arxiv_tool.search_papers(q, limit=limit)
            for p in ax:
                results.append({
                    'title': p.get('title'),
                    'abstract': p.get('abstract'),
                    'authors': p.get('authors') or [],
                    'year': p.get('year'),
                    'url': p.get('url'),
                    'source': 'arxiv',
                })
        resp = {'query': q, 'source': source, 'results': results}
        # Cache successful response for future requests (best-effort)
        try:
            _cache_set(key, resp)
        except Exception:
            pass
        return resp
    except httpx.HTTPStatusError as he:
        # Propagate upstream HTTP errors (e.g., 429 from Semantic Scholar)
        status = he.response.status_code if he.response is not None else 502
        raise HTTPException(status_code=status, detail=str(he))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
