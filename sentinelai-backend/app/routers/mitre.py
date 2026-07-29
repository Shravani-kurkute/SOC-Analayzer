from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.core.dependencies import get_current_user
from app.mitre.service import MitreService
from app.schemas.base import APIResponse, PaginatedResponse
from app.schemas.mitre import (
    CoverageStatisticResponse,
    MitreCoverageResponse,
    MitreMapRequest,
    MitreMapResponse,
    MitreMappingResponse,
    MitreTechniqueDetail,
    MitreTechniqueResponse,
)

router = APIRouter()


def get_mitre_service() -> MitreService:
    return MitreService()


@router.get("", response_model=APIResponse[dict[str, Any]])
async def mitre_root(
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    tactics = await service.list_tactics()
    return APIResponse(data={
        "tactics": len(tactics),
        "techniques": sum(t.get("technique_count", 0) for t in tactics),
        "message": "MITRE ATT&CK Mapping Engine",
        "version": "15.1",
    })


@router.get("/techniques", response_model=APIResponse[PaginatedResponse[MitreTechniqueResponse]])
async def list_techniques(
    tactic: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    items, total = await service.list_techniques(
        tactic=tactic, search=search, page=page, page_size=page_size,
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[MitreTechniqueResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    ))


@router.get("/tactics", response_model=APIResponse[list[dict[str, Any]]])
async def list_tactics(
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    tactics = await service.list_tactics()
    return APIResponse(data=tactics)


@router.get("/coverage", response_model=APIResponse[MitreCoverageResponse])
async def get_coverage(
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    coverage = await service.get_coverage()
    return APIResponse(data=MitreCoverageResponse(**coverage))


@router.post("/map", response_model=APIResponse[MitreMapResponse])
async def map_entity(
    request: MitreMapRequest,
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    mappings = await service.map_entity(
        mapped_type=request.mapped_type,
        mapped_id=request.mapped_id,
        mapped_name=request.mapped_name,
        context=request.context,
    )
    return APIResponse(
        message=f"Mapped to {len(mappings)} MITRE techniques",
        data=MitreMapResponse(
            mappings=[MitreMappingResponse.model_validate(m) for m in mappings],
            new_mappings=len(mappings),
            confidence_avg=0.7,
        ),
    )


@router.post("/seed", response_model=APIResponse[dict[str, Any]])
async def seed_techniques(
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    count = await service.seed_techniques()
    return APIResponse(
        message=f"Seeded {count} MITRE ATT&CK techniques",
        data={"seeded": count},
    )


@router.get("/search", response_model=APIResponse[PaginatedResponse[MitreTechniqueResponse]])
async def search_techniques(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    items, total = await service.search_techniques(q, page=page, page_size=page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return APIResponse(data=PaginatedResponse(
        items=[MitreTechniqueResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    ))


@router.get("/{technique_id}", response_model=APIResponse[MitreTechniqueDetail])
async def get_technique(
    technique_id: str,
    service: MitreService = Depends(get_mitre_service),
    _=Depends(get_current_user),
):
    detail = await service.get_technique_detail(technique_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Technique not found")
    return APIResponse(data=MitreTechniqueDetail(
        technique=MitreTechniqueResponse.model_validate(detail["technique"]),
        mappings=[MitreMappingResponse.model_validate(m) for m in detail["mappings"]],
        mapped_count=detail["mapped_count"],
        detection_coverage=detail["detection_coverage"],
        related_techniques=[MitreTechniqueResponse.model_validate(r) for r in detail["related_techniques"]],
    ))
