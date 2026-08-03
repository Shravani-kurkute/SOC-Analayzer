from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import AIInvestigationService
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.ai import (
    AIInvestigationListItem,
    AIInvestigationResponse,
    AIInvestigationStats,
    AIInvestigateRequest,
)
from app.schemas.base import APIResponse, PaginatedResponse

router = APIRouter()
service = AIInvestigationService()


@router.post("/investigate/{incident_id}", response_model=APIResponse[AIInvestigationResponse])
async def investigate_incident(
    incident_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    body: AIInvestigateRequest | None = None,
):
    provider = body.provider if body else None
    try:
        result = await service.investigate(incident_id, db, provider)
        return APIResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{incident_id}", response_model=APIResponse[AIInvestigationResponse])
async def get_investigation_report(
    incident_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    report = await service.get_report(incident_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="No investigation found for this incident")
    return APIResponse(data=report)


@router.get("/history", response_model=APIResponse[PaginatedResponse[AIInvestigationListItem]])
async def list_investigation_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await service.list_history(db, page, page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    ))


@router.delete("/history/{investigation_id}", response_model=APIResponse)
async def delete_investigation(
    investigation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deleted = await service.delete_history(investigation_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return APIResponse(message="Investigation deleted successfully")


@router.get("/stats", response_model=APIResponse[AIInvestigationStats])
async def get_ai_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stats = await service.get_stats(db)
    return APIResponse(data=stats)
