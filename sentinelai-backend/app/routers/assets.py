from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.asset_management.service import AssetManagementService
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.asset import (
    AssetCreate,
    AssetDetailResponse,
    AssetListItem,
    AssetRelationshipCreate,
    AssetResponse,
    AssetStats,
    AssetUpdate,
    AssetImportResult,
)
from app.schemas.base import APIResponse, PaginatedResponse

router = APIRouter()
service = AssetManagementService()


@router.get("/stats", response_model=APIResponse[AssetStats])
async def get_asset_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stats = await service.get_stats(db)
    return APIResponse(data=AssetStats(**stats))


@router.get("/search", response_model=APIResponse[PaginatedResponse[AssetListItem]])
async def search_assets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = await service.list_assets(
        db, page=page, page_size=page_size,
        search=q,
    )
    return APIResponse(data=PaginatedResponse(**result))


@router.post("/import/csv", response_model=APIResponse[AssetImportResult])
async def import_assets_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    content = (await file.read()).decode("utf-8")
    result = await service.import_csv(db, content, created_by=current_user.full_name)
    return APIResponse(data=AssetImportResult(**result.model_dump()), message=f"Imported {result.imported} assets")


@router.post("/import/json", response_model=APIResponse[AssetImportResult])
async def import_assets_json(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    content = (await file.read()).decode("utf-8")
    result = await service.import_json(db, content, created_by=current_user.full_name)
    return APIResponse(data=AssetImportResult(**result.model_dump()), message=f"Imported {result.imported} assets")


@router.post("/relationships", response_model=APIResponse[dict])
async def create_asset_relationship(
    body: AssetRelationshipCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    rel = await service.create_relationship(
        db, body.source_asset_id, body.target_asset_id,
        body.relationship_type, body.metadata_json,
    )
    return APIResponse(data=rel.to_dict(), message="Relationship created")


@router.get("", response_model=APIResponse[PaginatedResponse[AssetListItem]])
async def list_assets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    asset_type: str | None = Query(None),
    criticality: str | None = Query(None),
    status: str | None = Query(None),
    department: str | None = Query(None),
    owner: str | None = Query(None),
    os: str | None = Query(None),
    risk_level: str | None = Query(None),
    tag: str | None = Query(None),
):
    result = await service.list_assets(
        db, page=page, page_size=page_size, sort_by=sort_by,
        sort_order=sort_order, search=search, asset_type=asset_type,
        criticality=criticality, status=status, department=department,
        owner=owner, os=os, risk_level=risk_level, tag=tag,
    )
    return APIResponse(data=PaginatedResponse(**result))


@router.post("", response_model=APIResponse[AssetResponse], status_code=201)
async def create_asset(
    body: AssetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    asset = await service.create_asset(db, body, created_by=current_user.full_name)
    return APIResponse(data=AssetResponse(**asset.to_dict()), message="Asset created successfully")


@router.get("/{asset_id}", response_model=APIResponse[AssetDetailResponse])
async def get_asset(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    asset = await service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return APIResponse(data=AssetDetailResponse(**asset))


@router.put("/{asset_id}", response_model=APIResponse[AssetResponse])
async def update_asset(
    asset_id: str,
    body: AssetUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    asset = await service.update_asset(db, asset_id, body, changed_by=current_user.full_name)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return APIResponse(data=AssetResponse(**asset.to_dict()), message="Asset updated successfully")


@router.delete("/{asset_id}", response_model=APIResponse[dict])
async def delete_asset(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deleted = await service.delete_asset(db, asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Asset not found")
    return APIResponse(data={}, message="Asset deleted successfully")


@router.get("/{asset_id}/incidents", response_model=APIResponse[list])
async def get_asset_incidents(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    incidents = await service.get_related_incidents(db, asset_id)
    return APIResponse(data=[inc.to_dict() for inc in incidents])


@router.get("/{asset_id}/alerts", response_model=APIResponse[list])
async def get_asset_alerts(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    alerts = await service.get_related_alerts(db, asset_id)
    return APIResponse(data=[a.to_dict() for a in alerts])


@router.get("/{asset_id}/ioc", response_model=APIResponse[list])
async def get_asset_iocs(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    iocs = await service.get_related_iocs(db, asset_id)
    return APIResponse(data=[ioc.to_dict() for ioc in iocs])


@router.get("/{asset_id}/threat-intel", response_model=APIResponse[list])
async def get_asset_threat_intel(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    intel = await service.get_related_threat_intel(db, asset_id)
    return APIResponse(data=[t.to_dict() for t in intel])


@router.get("/{asset_id}/ai-reports", response_model=APIResponse[list])
async def get_asset_ai_reports(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    reports = await service.get_related_ai_reports(db, asset_id)
    return APIResponse(data=[r.to_dict() for r in reports])
