from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.ioc.service import IocService
from app.schemas.base import APIResponse, PaginatedResponse, PaginationParams
from app.schemas.ioc import IocEntryResponse, IocExtractResponse, IocSearchParams, IocStatsResponse
from app.core.dependencies import get_current_user

router = APIRouter()


def get_ioc_service() -> IocService:
    return IocService()


@router.post("/extract", response_model=APIResponse[IocExtractResponse])
async def extract_iocs(
    text: str = Query(..., description="Raw text to extract IOCs from"),
    source: str | None = Query(None, description="Optional log source identifier"),
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    entries = await service.extract_from_text(text, source)
    return APIResponse(
        success=True,
        message=f"Extracted {len(entries)} IOCs",
        data=IocExtractResponse(
            extracted=len(entries),
            new=sum(1 for e in entries if e.occurrences == 1),
            updated=sum(1 for e in entries if e.occurrences > 1),
            iocs=[IocEntryResponse.model_validate(e) for e in entries],
        ),
    )


@router.post("/extract-all", response_model=APIResponse[IocExtractResponse])
async def extract_all_iocs(
    events: list[dict[str, Any]] = Body(..., description="List of events or text objects to extract IOCs from"),
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    all_entries: list = []
    seen_keys: set[str] = set()
    for event in events:
        if isinstance(event, str) or "text" in event:
            text = event if isinstance(event, str) else event["text"]
            source = event.get("source") if isinstance(event, dict) else None
            entries = await service.extract_from_text(text, source)
        else:
            entries = await service.extract_from_event(event)
        for entry in entries:
            key = f"{entry.ioc_type}:{entry.normalized_value}"
            if key not in seen_keys:
                seen_keys.add(key)
                all_entries.append(entry)
    return APIResponse(
        success=True,
        message=f"Extracted {len(all_entries)} IOCs from {len(events)} sources",
        data=IocExtractResponse(
            extracted=len(all_entries),
            new=sum(1 for e in all_entries if e.occurrences == 1),
            updated=sum(1 for e in all_entries if e.occurrences > 1),
            iocs=[IocEntryResponse.model_validate(e) for e in all_entries],
        ),
    )


@router.post("/extract-from-event", response_model=APIResponse[IocExtractResponse])
async def extract_iocs_from_event(
    event: dict,
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    entries = await service.extract_from_event(event)
    return APIResponse(
        success=True,
        message=f"Extracted {len(entries)} IOCs from event",
        data=IocExtractResponse(
            extracted=len(entries),
            new=sum(1 for e in entries if e.occurrences == 1),
            updated=sum(1 for e in entries if e.occurrences > 1),
            iocs=[IocEntryResponse.model_validate(e) for e in entries],
        ),
    )


@router.get("", response_model=APIResponse[PaginatedResponse[IocEntryResponse]])
async def list_iocs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("last_seen"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    ioc_type: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    source_ip: str | None = Query(None),
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    filters = {k: v for k, v in {"ioc_type": ioc_type, "severity": severity, "status": status, "source_ip": source_ip}.items() if v}
    items, total = await service.list_iocs(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order, filters=filters)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[IocEntryResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    ))


@router.get("/stats", response_model=APIResponse[IocStatsResponse])
async def ioc_stats(
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    stats = await service.get_stats()
    return APIResponse(data=IocStatsResponse(**stats))


@router.get("/search", response_model=APIResponse[PaginatedResponse[IocEntryResponse]])
async def search_iocs(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    items, total = await service.search_iocs(q, page=page, page_size=page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[IocEntryResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    ))


@router.get("/{ioc_id}", response_model=APIResponse[IocEntryResponse])
async def get_ioc(
    ioc_id: str,
    service: IocService = Depends(get_ioc_service),
    _=Depends(get_current_user),
):
    entry = await service.get_ioc(ioc_id)
    if not entry:
        raise HTTPException(status_code=404, detail="IOC not found")
    return APIResponse(data=IocEntryResponse.model_validate(entry))
