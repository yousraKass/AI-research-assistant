from fastapi import APIRouter, Query, HTTPException
from typing import List

import httpx
from ..tools import semantic_scholar
from ..tools import arxiv as arxiv_tool

router = APIRouter()


@router.get('/papers/search')
async def papers_search(q: str = Query(..., min_length=1), source: str = Query('semantic_scholar')):
    """Search papers from a selected source.

    Query params:
    - q: query string
    - source: 'semantic_scholar' | 'arxiv' | 'all'
    """
    source = source.lower()
    try:
        results = []
        if source in ('semantic_scholar', 'all'):
            ss = semantic_scholar.search_papers(q, limit=10)
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
            ax = arxiv_tool.search_papers(q, limit=10)
            for p in ax:
                results.append({
                    'title': p.get('title'),
                    'abstract': p.get('abstract'),
                    'authors': p.get('authors') or [],
                    'year': p.get('year'),
                    'url': p.get('url'),
                    'source': 'arxiv',
                })
        return {'query': q, 'source': source, 'results': results}
    except httpx.HTTPStatusError as he:
        # Propagate upstream HTTP errors (e.g., 429 from Semantic Scholar)
        status = he.response.status_code if he.response is not None else 502
        raise HTTPException(status_code=status, detail=str(he))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
