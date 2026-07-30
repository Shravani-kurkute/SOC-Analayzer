from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, get_db
from app.schemas.base import APIResponse, PaginatedResponse
from app.schemas.threat_intel import (
    LookupRequest, ThreatIntelResponse, ThreatIntelStatsResponse,
)
from app.services.threat_intel.service import ThreatIntelligenceService

router = APIRouter()
ti_service = ThreatIntelligenceService()


@router.post("/lookup", response_model=APIResponse[ThreatIntelResponse])
async def lookup_ioc(
    body: LookupRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _=Depends(get_current_user),
):
    if not body.ioc_type or not body.ioc_value:
        raise HTTPException(status_code=400, detail="ioc_type and ioc_value are required")
    result = await ti_service.lookup(body.ioc_type, body.ioc_value, db)
    return APIResponse(data=ThreatIntelResponse(**result))


@router.get("", response_model=APIResponse[PaginatedResponse[dict[str, Any]]])
async def list_threat_intel(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("last_analysis"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    ioc_type: str | None = Query(None),
    is_malicious: bool | None = Query(None),
    q: str | None = Query(None),
    _=Depends(get_current_user),
):
    filters = {k: v for k, v in {"ioc_type": ioc_type, "is_malicious": is_malicious, "q": q}.items() if v is not None}
    items, total = await ti_service.list_intel(
        page=page, page_size=page_size,
        sort_by=sort_by, sort_order=sort_order,
        filters=filters,
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[
            {
                "id": i.id, "ioc_type": i.ioc_type, "ioc_value": i.ioc_value,
                "normalized_value": i.normalized_value,
                "reputation_score": i.reputation_score,
                "is_malicious": i.is_malicious,
                "malicious_count": i.malicious_count,
                "country": i.country, "asn": i.asn,
                "last_analysis": i.last_analysis.isoformat() if i.last_analysis else None,
                "tags": i.tags,
            }
            for i in items
        ],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    ))


@router.get("/stats", response_model=APIResponse[ThreatIntelStatsResponse])
async def threat_intel_stats(
    _=Depends(get_current_user),
):
    stats = await ti_service.get_stats()
    return APIResponse(data=ThreatIntelStatsResponse(**stats))


@router.get("/{ioc_id}", response_model=APIResponse[ThreatIntelResponse])
async def get_threat_intel(
    ioc_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _=Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.threat_intel import ThreatIntel
    result = await db.execute(select(ThreatIntel).where(ThreatIntel.id == ioc_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Threat intelligence entry not found")
    results = await ti_service._get_provider_results(entry.id, db)
    resp = ti_service._build_response(entry, results)
    return APIResponse(data=ThreatIntelResponse(**resp))
