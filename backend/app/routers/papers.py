from fastapi import APIRouter, Query, HTTPException
import httpx

from ..services import papers as papers_service


router = APIRouter()


@router.get('/papers/search')
async def papers_search(q: str = Query(..., min_length=1), source: str = Query('semantic_scholar'), limit: int = Query(10, ge=1, le=100)):
    """Search papers from a selected source.

    Query params:
    - q: query string
    - source: 'semantic_scholar' | 'arxiv' | 'all'
    """
    try:
        resp = papers_service.search(q, source=source, limit=limit)
        return resp
    except httpx.HTTPStatusError as he:
        status = he.response.status_code if he.response is not None else 502
        raise HTTPException(status_code=status, detail=str(he))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
