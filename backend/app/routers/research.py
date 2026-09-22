from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional

from ..services import research as research_service

router = APIRouter()


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: Optional[int] = Field(6, ge=1, le=20)


@router.post('/research')
async def run_research(body: ResearchRequest = Body(...)):
    try:
        result = research_service.research(body.query, limit=body.limit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
