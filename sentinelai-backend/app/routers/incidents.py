from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.incident_response.service import IncidentResponseService
from app.models.user import User
from app.schemas.base import APIResponse, PaginatedResponse
from app.schemas.incident_response import (
    IncidentAssign,
    IncidentClose,
    IncidentCommentCreate,
    IncidentCommentResponse,
    IncidentCommentUpdate,
    IncidentCreate,
    IncidentDetailResponse,
    IncidentEvidenceCreate,
    IncidentEvidenceResponse,
    IncidentListItem,
    IncidentTaskCreate,
    IncidentTaskResponse,
    IncidentTaskUpdate,
    IncidentUpdate,
)

router = APIRouter()
service = IncidentResponseService()


@router.post("", response_model=APIResponse[IncidentDetailResponse])
async def create_incident(
    body: IncidentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.create_incident(
        db,
        title=body.title,
        severity=body.severity,
        created_by=current_user.full_name,
        description=body.description,
        category=body.category,
        alert_ids=body.alert_ids,
        asset_ids=body.asset_ids,
    )
    return APIResponse(data=result)


@router.get("", response_model=APIResponse[PaginatedResponse[IncidentListItem]])
async def list_incidents(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    assignee_id: str | None = Query(None),
    search: str | None = Query(None),
):
    items, total = await service.list_incidents(
        db, page, page_size, sort_by, sort_order,
        severity, status, assignee_id, search,
    )
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


@router.get("/stats", response_model=APIResponse[dict[str, Any]])
async def get_incident_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stats = await service.get_stats(db)
    return APIResponse(data=stats)


@router.get("/{incident_id}", response_model=APIResponse[IncidentDetailResponse])
async def get_incident(
    incident_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.get_incident(db, incident_id)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=result)


@router.put("/{incident_id}", response_model=APIResponse[IncidentDetailResponse])
async def update_incident(
    incident_id: str,
    body: IncidentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.update_incident(
        db, incident_id, current_user.full_name,
        **body.model_dump(exclude_none=True),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=result)


@router.post("/{incident_id}/assign", response_model=APIResponse[IncidentDetailResponse])
async def assign_incident(
    incident_id: str,
    body: IncidentAssign,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        result = await service.assign_incident(db, incident_id, body.user_id, current_user.full_name)
        if not result:
            raise HTTPException(status_code=404, detail="Incident not found")
        return APIResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{incident_id}/close", response_model=APIResponse[IncidentDetailResponse])
async def close_incident(
    incident_id: str,
    body: IncidentClose,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.close_incident(
        db, incident_id, current_user.full_name,
        resolution=body.resolution, notes=body.notes,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return APIResponse(data=result)


@router.post("/{incident_id}/comment", response_model=APIResponse[IncidentCommentResponse])
async def add_comment(
    incident_id: str,
    body: IncidentCommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.add_comment(
        db, incident_id, current_user.id, current_user.full_name, body.content,
    )
    return APIResponse(data=result)


@router.put("/{incident_id}/comment/{comment_id}", response_model=APIResponse[IncidentCommentResponse])
async def edit_comment(
    incident_id: str,
    comment_id: str,
    body: IncidentCommentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.edit_comment(db, comment_id, current_user.id, body.content)
    if not result:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    return APIResponse(data=result)


@router.delete("/{incident_id}/comment/{comment_id}", response_model=APIResponse)
async def delete_comment(
    incident_id: str,
    comment_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deleted = await service.delete_comment(db, comment_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    return APIResponse(message="Comment deleted")


@router.post("/{incident_id}/task", response_model=APIResponse[IncidentTaskResponse])
async def create_task(
    incident_id: str,
    body: IncidentTaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.create_task(
        db, incident_id, body.title, current_user.full_name,
        description=body.description, priority=body.priority,
        assignee_id=body.assignee_id, due_date=body.due_date,
    )
    return APIResponse(data=result)


@router.get("/{incident_id}/task", response_model=APIResponse[list[IncidentTaskResponse]])
async def list_tasks(
    incident_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    from app.incident_response.tasks import get_tasks
    tasks = await get_tasks(db, incident_id)
    return APIResponse(data=[service._task_to_dict(t) for t in tasks])


@router.patch("/{incident_id}/task/{task_id}", response_model=APIResponse[IncidentTaskResponse])
async def update_task(
    incident_id: str,
    task_id: str,
    body: IncidentTaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.update_task(
        db, task_id, current_user.full_name,
        **body.model_dump(exclude_none=True),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return APIResponse(data=result)


@router.post("/{incident_id}/evidence", response_model=APIResponse[IncidentEvidenceResponse])
async def upload_evidence(
    incident_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
    description: str | None = Query(None),
):
    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="Empty file")

    result = await service.upload_evidence(
        db, incident_id, file.filename or "unnamed",
        file_data, current_user.full_name, description,
    )
    return APIResponse(data=result)


@router.get("/{incident_id}/evidence", response_model=APIResponse[list[IncidentEvidenceResponse]])
async def list_evidence(
    incident_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    from app.incident_response.evidence import get_evidence_list
    evidence = await get_evidence_list(db, incident_id)
    return APIResponse(data=[service._evidence_to_dict(e) for e in evidence])


@router.delete("/{incident_id}/evidence/{evidence_id}", response_model=APIResponse)
async def delete_evidence(
    incident_id: str,
    evidence_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    from app.incident_response.evidence import delete_evidence
    deleted = await delete_evidence(db, evidence_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return APIResponse(message="Evidence deleted")
